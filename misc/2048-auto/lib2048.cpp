/* The fundamental trick: the 4x4 board is represented as a 64-bit word,
 * with each board square packed into a single 4-bit nibble.
 * 
 * The maximum possible board value that can be supported is 32768 (2^15), but
 * this is a minor limitation as achieving 65536 is highly unlikely under normal circumstances.
 * 
 * The space and computation savings from using this representation should be significant.
 * 
 * The nibble shift can be computed as (r,c) -> shift (4*r + c). That is, (0,0) is the LSB.
 */

#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <time.h>
#include <algorithm>
#include <unordered_map>
#include <signal.h>
#include <pthread.h>
extern "C" {
	int nprocs();
}

static inline unsigned unif_random(unsigned n) {
    static int seeded = 0;
    if(!seeded) {
        int fd = open("/dev/urandom", O_RDONLY);
        unsigned short seed[3];
        if(fd < 0 || read(fd, seed, sizeof(seed)) < (int)sizeof(seed)) {
            srand48(time(NULL));
        } else {
            seed48(seed);
        }
        if(fd >= 0) {
            close(fd);
		}
        seeded = 1;
    }
    return (int)(drand48() * n);
}

typedef uint64_t board_t;
typedef uint16_t row_t;

//store the depth at which the heuristic was recorded as well as the actual heuristic
struct trans_table_entry_t{
    uint8_t depth;
    float heuristic;
};

typedef std::unordered_map<board_t, trans_table_entry_t> trans_table_t;
static const board_t ROW_MASK = 0xFFFFULL;
static const board_t COL_MASK = 0x000F000F000F000FULL;

static inline void print_board(board_t board) {
    int i,j;
    for(i=0; i<4; i++) {
        for(j=0; j<4; j++) {
            uint8_t powerVal = (board) & 0xf;
            printf("%6u", (powerVal == 0) ? 0 : 1 << powerVal);
            board >>= 4;
        }
        printf("\n");
    }
    printf("\n");
}

static inline board_t unpack_col(row_t row) {
    board_t tmp = row;
    return (tmp | (tmp << 12ULL) | (tmp << 24ULL) | (tmp << 36ULL)) & COL_MASK;
}

static inline row_t reverse_row(row_t row) {
    return (row >> 12) | ((row >> 4) & 0x00F0)  | ((row << 4) & 0x0F00) | (row << 12);
}

/*
Transpose rows/columns in a board:
   0123       048c
   4567  -->  159d
   89ab       26ae
   cdef       37bf
*/
static inline board_t transpose(board_t x)
{
    board_t a1 = x & 0xF0F00F0FF0F00F0FULL;
    board_t a2 = x & 0x0000F0F00000F0F0ULL;
    board_t a3 = x & 0x0F0F00000F0F0000ULL;
    board_t a = a1 | (a2 << 12) | (a3 >> 12);
    board_t b1 = a & 0xFF00FF0000FF00FFULL;
    board_t b2 = a & 0x00FF00FF00000000ULL;
    board_t b3 = a & 0x00000000FF00FF00ULL;
    return b1 | (b2 >> 24) | (b3 << 24);
}

// Count the number of empty positions (= zero nibbles) in a board.
// Precondition: the board cannot be fully empty.
static int count_empty(board_t x)
{
    x |= (x >> 2) & 0x3333333333333333ULL;
    x |= (x >> 1);
    x = ~x & 0x1111111111111111ULL;
    // At this point each nibble is:
    //  0 if the original nibble was non-zero
    //  1 if the original nibble was zero
    // Next sum them all
    x += x >> 32;
    x += x >> 16;
    x += x >>  8;
    x += x >>  4; // this can overflow to the next nibble if there were 16 empty positions
    return x & 0xf;
}

/* We can perform state lookups one row at a time by using arrays with 65536 entries. */

/* Move tables. Each row or compressed column is mapped to (oldrow^newrow) assuming row/col 0.
 *
 * Thus, the value is 0 if there is no move, and otherwise equals a value that can easily be
 * xor'ed into the current board state to update the board. */
typedef struct {
	row_t row_left_table [65536];
	row_t row_right_table[65536];
	board_t col_up_table[65536];
	board_t col_down_table[65536];
	float heur_score_table[65536];
	float score_table[65536];
} table_data_t;

// Heuristic scoring settings
static const float SCORE_LOST_PENALTY = 200000.0f;
static const float SCORE_MONOTONICITY_POWER = 4.0f;
static const float SCORE_MONOTONICITY_WEIGHT = 47.0f;
static const float SCORE_SUM_POWER = 3.5f;
static const float SCORE_SUM_WEIGHT = 11.0f;
static const float SCORE_MERGES_WEIGHT = 700.0f;
static const float SCORE_EMPTY_WEIGHT = 270.0f;

void init_tables(table_data_t *table) {
    for (unsigned row = 0; row < 65536; ++row) {
        unsigned line[4] = {
                (row >>  0) & 0xf,
                (row >>  4) & 0xf,
                (row >>  8) & 0xf,
                (row >> 12) & 0xf
        };

        // Score
        float score = 0.0f;
        for (int i = 0; i < 4; ++i) {
            int rank = line[i];
            if (rank >= 2) {
                // the score is the total sum of the tile and all intermediate merged tiles
                score += (rank - 1) * (1 << rank);
            }
        }
        (table->score_table)[row] = score;

        // Heuristic score
        float sum = 0;
        int empty = 0;
        int merges = 0;

        int prev = 0;
        int counter = 0;
        for (int i = 0; i < 4; ++i) {
            int rank = line[i];
            sum += pow(rank, SCORE_SUM_POWER);
            if (rank == 0) {
                empty++;
            } else {
                if (prev == rank) {
                    counter++;
                } else if (counter > 0) {
                    merges += 1 + counter;
                    counter = 0;
                }
                prev = rank;
            }
        }
        if (counter > 0) {
            merges += 1 + counter;
        }

        float monotonicity_left = 0;
        float monotonicity_right = 0;
        for (int i = 1; i < 4; ++i) {
            if (line[i-1] > line[i]) {
                monotonicity_left += pow(line[i-1], SCORE_MONOTONICITY_POWER) - pow(line[i], SCORE_MONOTONICITY_POWER);
            } else {
                monotonicity_right += pow(line[i], SCORE_MONOTONICITY_POWER) - pow(line[i-1], SCORE_MONOTONICITY_POWER);
            }
        }

        (table->heur_score_table)[row] = SCORE_LOST_PENALTY +
            SCORE_EMPTY_WEIGHT * empty +
            SCORE_MERGES_WEIGHT * merges -
            SCORE_MONOTONICITY_WEIGHT * std::min(monotonicity_left, monotonicity_right) -
            SCORE_SUM_WEIGHT * sum;

        // execute a move to the left
        for (int i = 0; i < 3; ++i) {
            int j;
            for (j = i + 1; j < 4; ++j) {
                if (line[j] != 0) break;
            }
            if (j == 4) break; // no more tiles to the right

            if (line[i] == 0) {
                line[i] = line[j];
                line[j] = 0;
                i--; // retry this entry
            } else if (line[i] == line[j]) {
                if(line[i] != 0xf) {
                    /* Pretend that 32768 + 32768 = 32768 (representational limit). */
                    line[i]++;
                }
                line[j] = 0;
            }
        }

        row_t result = (line[0] <<  0) |
                       (line[1] <<  4) |
                       (line[2] <<  8) |
                       (line[3] << 12);
        row_t rev_result = reverse_row(result);
        unsigned rev_row = reverse_row(row);

        (table->row_left_table)[row] = row ^ result;
        (table->row_right_table)[rev_row] = rev_row ^ rev_result;
        (table->col_up_table)[row] = unpack_col(row) ^ unpack_col(result);
        (table->col_down_table)[rev_row] = unpack_col(rev_row) ^ unpack_col(rev_result);
    }
}

/* Execute a move. */
static inline board_t execute_move(table_data_t *table, int move, board_t board) {
    board_t ret = board, t;
    switch(move) {
		case 0: // up
			t = transpose(board);
			ret ^= (table->col_up_table)[(t >>  0) & ROW_MASK] <<  0;
			ret ^= (table->col_up_table)[(t >> 16) & ROW_MASK] <<  4;
			ret ^= (table->col_up_table)[(t >> 32) & ROW_MASK] <<  8;
			ret ^= (table->col_up_table)[(t >> 48) & ROW_MASK] << 12;
			return ret;
		case 1: // down
			t = transpose(board);
			ret ^= (table->col_down_table)[(t >>  0) & ROW_MASK] <<  0;
			ret ^= (table->col_down_table)[(t >> 16) & ROW_MASK] <<  4;
			ret ^= (table->col_down_table)[(t >> 32) & ROW_MASK] <<  8;
			ret ^= (table->col_down_table)[(t >> 48) & ROW_MASK] << 12;
			return ret;
		case 2: // left
			ret ^= board_t((table->row_left_table)[(board >>  0) & ROW_MASK]) <<  0;
			ret ^= board_t((table->row_left_table)[(board >> 16) & ROW_MASK]) << 16;
			ret ^= board_t((table->row_left_table)[(board >> 32) & ROW_MASK]) << 32;
			ret ^= board_t((table->row_left_table)[(board >> 48) & ROW_MASK]) << 48;
			return ret;
		case 3: // right
			ret ^= board_t((table->row_right_table)[(board >>  0) & ROW_MASK]) <<  0;
			ret ^= board_t((table->row_right_table)[(board >> 16) & ROW_MASK]) << 16;
			ret ^= board_t((table->row_right_table)[(board >> 32) & ROW_MASK]) << 32;
			ret ^= board_t((table->row_right_table)[(board >> 48) & ROW_MASK]) << 48;
			return ret;
		default:
			return ~0ULL;
    }
}
static inline int get_max_rank(board_t board) {
    int maxrank = 0;
    while (board) {
        maxrank = std::max(maxrank, int(board & 0xf));
        board >>= 4;
    }
    return maxrank;
}
static inline int count_distinct_tiles(board_t board) {
    uint16_t bitset = 0;
    while (board) {
        bitset |= 1<<(board & 0xf);
        board >>= 4;
    }

    // Don't count empty tiles.
    bitset >>= 1;

    int count = 0;
    while (bitset) {
        bitset &= bitset - 1;
        count++;
    }
    return count;
}

/* Optimizing the game */
struct eval_state {
    trans_table_t trans_table; // transposition table, to cache previously-seen moves
    int maxdepth;
    int curdepth;
    int cachehits;
    unsigned long moves_evaled;
    int depth_limit;
    eval_state() : maxdepth(0), curdepth(0), cachehits(0), moves_evaled(0), depth_limit(0) {
    }
};

// score over all possible moves
static float score_move_node(table_data_t *table, eval_state &state, board_t board, float cprob);
// score over all possible tile choices and placements
static float score_tilechoose_node(table_data_t *table, eval_state &state, board_t board, float cprob);

static float score_helper(board_t board, const float* table) {
    return table[(board >>  0) & ROW_MASK] +
           table[(board >> 16) & ROW_MASK] +
           table[(board >> 32) & ROW_MASK] +
           table[(board >> 48) & ROW_MASK];
}

// score a single board heuristically
static float score_heur_board(table_data_t *table, board_t board) {
    return score_helper(          board , table->heur_score_table) +
           score_helper(transpose(board), table->heur_score_table);
}

// score a single board actually (adding in the score from spawned 4 tiles)
static float score_board(table_data_t *table, board_t board) {
    return score_helper(board, table->score_table);
}

// Statistics and controls
// cprob: cumulative probability
// don't recurse into a node with a cprob less than this threshold
static const float CPROB_THRESH_BASE = 0.0001f;
static const int CACHE_DEPTH_LIMIT  = 15;

static float score_tilechoose_node(table_data_t *table, eval_state &state, board_t board, float cprob) {
    if (cprob < CPROB_THRESH_BASE || state.curdepth >= state.depth_limit) {
        state.maxdepth = std::max(state.curdepth, state.maxdepth);
        return score_heur_board(table, board);
    }
    if (state.curdepth < CACHE_DEPTH_LIMIT) {
        const trans_table_t::iterator &i = state.trans_table.find(board);
        if (i != state.trans_table.end()) {
            trans_table_entry_t entry = i->second;
            /*
            return heuristic from transposition table only if it means that
            the node will have been evaluated to a minimum depth of state.depth_limit.
            This will result in slightly fewer cache hits, but should not impact the
            strength of the ai negatively.
            */
            if(entry.depth <= state.curdepth)
            {
                state.cachehits++;
                return entry.heuristic;
            }
        }
    }

    int num_open = count_empty(board);
    cprob /= num_open;

    float res = 0.0f;
    board_t tmp = board;
    board_t tile_2 = 1;
    while (tile_2) {
        if ((tmp & 0xf) == 0) {
            res += score_move_node(table, state, board |  tile_2      , cprob * 0.9f) * 0.9f;
            res += score_move_node(table, state, board | (tile_2 << 1), cprob * 0.1f) * 0.1f;
        }
        tmp >>= 4;
        tile_2 <<= 4;
    }
    res = res / num_open;

    if (state.curdepth < CACHE_DEPTH_LIMIT) {
        trans_table_entry_t entry = {static_cast<uint8_t>(state.curdepth), res};
        state.trans_table[board] = entry;
    }

    return res;
}
static float score_move_node(table_data_t *table, eval_state &state, board_t board, float cprob) {
    float best = 0.0f;
    state.curdepth++;
    for (int move = 0; move < 4; ++move) {
        board_t newboard = execute_move(table, move, board);
        state.moves_evaled++;

        if (board != newboard) {
            best = std::max(best, score_tilechoose_node(table, state, newboard, cprob));
        }
    }
    state.curdepth--;

    return best;
}
static float _score_toplevel_move(table_data_t *table, eval_state &state, board_t board, int move) {
    //int maxrank = get_max_rank(board);
    board_t newboard = execute_move(table, move, board);
    if (board == newboard) {
        return 0;
	}
    return score_tilechoose_node(table, state, newboard, 1.0f) + 1e-6;
}
float score_toplevel_move(table_data_t *table, board_t board, int move) {
    float res;
    //struct timeval start, finish;
    //double elapsed;
    eval_state state;
    state.depth_limit = std::max(3, count_distinct_tiles(board) - 2);

    //gettimeofday(&start, NULL);
    res = _score_toplevel_move(table, state, board, move);
    //gettimeofday(&finish, NULL);

	/*
    elapsed = (finish.tv_sec - start.tv_sec);
    elapsed += (finish.tv_usec - start.tv_usec) / 1000000.0;

    printf("Move %d: result %f: eval'd %ld moves (%d cache hits, %d cache size) in %.2f seconds (maxdepth=%d)\n", move, res,
        state.moves_evaled, state.cachehits, (int)state.trans_table.size(), elapsed, state.maxdepth);
	*/
    return res;
}

/* Find the best move for a given board. */
extern "C" {
	int find_best_move(board_t board) {
		static table_data_t table;
		static bool active = false;
		//Init table when called at the first time
		if (!active) {
			init_tables(&table);
			active = true;
		}

		int move;
		float best = 0;
		int bestmove = -1;

		//print_board(board);
		//printf("Current scores: heur %.0f, actual %.0f\n", score_heur_board(board), score_board(board));

		for(move=0; move<4; move++) {
			float res = score_toplevel_move(&table, board, move);
			if(res > best) {
				best = res;
				bestmove = move;
			}
		}
		return bestmove;
	}
	int __init__(){
		return 0;
	}
}

