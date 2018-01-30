#include <stdio.h>
#include <stdlib.h>

#define HELP_TEXT "Usage: %s sudoku_file\n"

#define CHECK_SUDOKU "Checking sudoku... "
#define CHECK_SUDOKU_PASSED "Passed\nStart calculatng...\n"
#define CALC_FINISHED "Calculation finished.\n"

#define OPEN_FILE_FAILED "Unable to open file.\n"
#define INCONSISTENT_NUM_ROW "Inconsistent number at row %d.\n"
#define INCONSISTENT_NUM_COL "Inconsistent number at column %d.\n"
#define INCONSISTENT_NUM_AREA "Inconsistent number at area %d.\n"
#define NO_ANSWER_POS "No answer at row %d, column %d.\n"
#define NO_ANSWER "No answer\n"

static int candl, board[9][9] = {
	{0,0,0,0,0,0,0,0,0},
	{0,0,0,0,0,0,0,0,0},
	{0,0,0,0,0,0,0,0,0},
	{0,0,0,0,0,0,0,0,0},
	{0,0,0,0,0,0,0,0,0},
	{0,0,0,0,0,0,0,0,0},
	{0,0,0,0,0,0,0,0,0},
	{0,0,0,0,0,0,0,0,0},
	{0,0,0,0,0,0,0,0,0},
}, cand[81][3];

void read_sudoku(char *filename){
	int x, y;
	FILE *fp;
	fp = fopen(filename, "r");
	if (!fp){
		printf(OPEN_FILE_FAILED);
		exit(1);
	}
	for (y = 0; y < 9; y++){
		for (x = 0; x < 9; x++){
			fscanf(fp, "%d", &(board[y][x]));
		}
	}
	fclose(fp);
}
void printboard(){
	int x, y;
	for (y = 0; y < 9; y++){
		for (x = 0; x < 9; x++){
			printf("%d ", board[y][x]);
			if (2 == (x % 3)){
				printf(" ");
			}
		}
		puts("");
		if (2 == (y % 3)){
			puts("");
		}
	}
}
void check_sudoku(){
	int x, y, area, ax, ay, nums, n;
	
	//Check inconsistent numbers
	for (y = 0; y < 9; y++){
		nums = 0;
		for (x = 0; x < 9; x++){
			n = board[y][x];
			if (n) {
				if (nums & (1 << n)){
					printf(INCONSISTENT_NUM_ROW, y+1);
					exit(1);
				} else {
					nums |= (1 << n);
				}
			}
		}
	}
	
	for (x = 0; x < 9; x++){
		nums = 0;
		for (y = 0; y < 9; y++){
			n = board[y][x];
			if (n) {
				if (nums & (1 << n)){
					printf(INCONSISTENT_NUM_COL, x+1);
					exit(1);
				} else {
					nums |= (1 << n);
				}
			}
		}
	}
	
	for (area = 0; area < 9; area++) {
		ax = (area % 3) * 3;
		ay = (int)(area / 3) * 3;
		nums = 0;
		for (y = 0; y < 3; y++){
			for (x = 0; x < 3; x++){
				n = board[ay + y][ax + x];
				if (n) {
					if (nums & (1 << n)){
						printf(INCONSISTENT_NUM_AREA, area+1);
						exit(1);
					} else {
						nums |= (1 << n);
					}
				}
			}
		}
	}
}

int getcand(int x, int y){
	int nums = 0, ox, oy, i, j;
	for (i = 0; i < 9; i++){
		nums |= ((1 << board[y][i]) | (1 << board[i][x]));
	}
	ox = (int)(x / 3) * 3; oy = (int)(y / 3) * 3;
	for (i = 0; i < 3; i++){
		for (j = 0; j < 3; j++){
			nums |= (1 << board[oy+i][ox+j]);
		}
	}
	return (~nums) & 0x3fe;
}
int getnextnum(int n, int c){
	n++;
	while (n <= 9) {
		if (c & (1 << n)){
			return n;
		}
		n++;
	}
	return 0;
}
int checknum(int x, int y, int n){
	int i, x1, y1, ax = (int)(x / 3) * 3, ay = (int)(y / 3) * 3;
	for (i = 0; i < 9; i++){
		if (x != i && board[y][i] == n){
			return 0;
		} else if (y != i && board[i][x] == n){
			return 0;
		}
	}
	for (y1 = ay; y1 < ay + 3; y1++){
		for (x1 = ax; x1 < ax + 3; x1++){
			if (x1 != x && y1 != y && board[y1][x1] == n){
				return 0;
			}
		}
	}
	return 1;
}
void updatecandl(){
	int x, y, c;
	candl = 0;
	for (y = 0; y < 9; y++){
		for (x = 0; x < 9; x++){
			if (board[y][x] != 0){
				continue;
			}
			c = getcand(x, y);
			if (c == 0){
				printf(NO_ANSWER_POS, y+1, x+1);
				exit(1);
			}
			cand[candl][0] = x;
			cand[candl][1] = y;
			cand[candl][2] = c;
			candl++;
		}
	}
}
int calc_step1(){
	int i, x, y, cn, status = 0;
	updatecandl();
	while (!status && candl > 0){
		status = 1;
		for (i = 0; i < candl; i++){
			cn = cand[i][2];
			if (0 == (cn & (cn - 1))){
				x = cand[i][0]; y = cand[i][1];
				board[y][x] = getnextnum(0, cn);
				status = 0;
			}
		}
		if (!status) {
			updatecandl();
		}
	}
	return ((candl > 0) ? 0 : 1);
}
void calc_step2(){
	int sl = 0, s[81], x, y;
	s[0] = getnextnum(0, cand[0][2]);
	while (sl < candl){
		x = cand[sl][0]; y = cand[sl][1];
		if (0 == s[sl]){
			board[y][x] = 0; sl--;
			s[sl] = getnextnum(s[sl], cand[sl][2]);
		} else if(checknum(x, y, s[sl])){
			board[y][x] = s[sl]; sl++;
			if (sl < candl){
				s[sl] = getnextnum(0, cand[sl][2]);
			}
		} else {
			s[sl] = getnextnum(s[sl], cand[sl][2]);
		}
		//printboard();
	}
}

int main(int argc, char *argv[]){
	if (argc < 2){
		printf(HELP_TEXT, argv[0]);
		exit(1);
	}
	read_sudoku(argv[1]);
	printf(CHECK_SUDOKU);
	check_sudoku();
	printf(CHECK_SUDOKU_PASSED);
	if (calc_step1()) {
		printboard();
		printf(CALC_FINISHED);
		return 0;
	}
	calc_step2();
	printf(CALC_FINISHED);
	printboard();
	return 0;
}
