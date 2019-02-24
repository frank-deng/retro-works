#include <stdio.h>
#include <dos.h>
#include <stdlib.h>
#include <time.h>
#include <conio.h>

#define FILE_SAVE "2048.sav"

typedef unsigned char uint8_t;
typedef unsigned short uint16_t;
#define BOARD_W 4
#define BOARD_H 4
#define BOARD_SIZE 16
typedef struct _game2048_t{
	unsigned short board[BOARD_H][BOARD_W];
	unsigned long score;
	unsigned char status;
}game2048_t;

/* Graphic functions */
union REGS inregs, outregs;
void initscr(){
  directvideo=1;
  _setcursortype(_NOCURSOR);
	clrscr();
}
void endscr(){
  gotoxy(0,0);
  textattr(0x07);
  clrscr();
  _setcursortype(_NORMALCURSOR);
}
void drawframe(){
	int i;
  textattr(0x0e);
  gotoxy(29,6);
	cprintf("Score: ");

  textattr(0x09);
  gotoxy(28,8);
	cprintf("\xc9");
	for (i = 0; i < 24; i++){
		cprintf("\xcd");
	}
	cprintf("\xbb");

	for (i = 0; i < 9; i++){
    gotoxy(28, 9+i);
		cprintf("\xba");
    gotoxy(28+25, 9+i);
		cprintf("\xba");
	}

  gotoxy(28,18);
	cprintf("\xc8");
	for (i = 0; i < 24; i++){
		cprintf("\xcd");
	}
	cprintf("\xbc");
}
void drawboard(game2048_t* game){
	int x, y;
	char buf[16] = {'\0'};
	for (y = 0; y < BOARD_H; y++){
		for (x = 0; x < BOARD_W; x++){
      gotoxy(29+6*x, 10+(y<<1));
      textattr(0x0f);
			if (game->board[y][x]) {
				sprintf(buf, "%5u ", game->board[y][x]);
				cprintf(buf);
			} else {
				cprintf("    . ");
			}
		}
	}
	sprintf(buf, "%lu", game->score);
  textattr(0x0e);
  gotoxy(36,6);
	cprintf(buf);
	if (game->status){
    textattr(0x0c);
    gotoxy(36,20);
		cprintf("GAME  OVER");
	}
}

/* Load and save */
int game2048_load(game2048_t* game, char* filename){
  int i;
  FILE *fp; uint16_t *p_board = game->board;
  fp = fopen(filename, "rb");
  if(NULL==fp){
    return 0;
  }
  fseek(fp,0,SEEK_SET);
  fread(game, sizeof(game2048_t), 1, fp);
  fclose(fp);
  return 1;
}
void game2048_save(game2048_t* game, char* filename){
  int i;
  FILE *fp; uint16_t *p_board = game->board;
  fp = fopen(filename, "wb");
  if(NULL==fp){
    return;
  }
  fseek(fp,0,SEEK_SET);
  fwrite(game, sizeof(game2048_t), 1, fp);
  fclose(fp);
}

/* Game functions */
int game2048_update(game2048_t* game);
void game2048_init(game2048_t* game){
	int i;
	uint16_t *p_board = game->board;
	srand(time(NULL));
	for (i = 0; i < BOARD_SIZE; i++, p_board++) {
		*p_board = 0;
	}
	game->score = 0;
	game->status = 0;
  if(!game2048_load(game, FILE_SAVE)){
	  game2048_update(game);
  }
}
void game2048_quit(game2048_t* game){
	if(0 == game->status){
    game2048_save(game, FILE_SAVE);
  }else{
    unlink(FILE_SAVE);
  }
}
int game2048_update(game2048_t* game){
	struct empty_space_t {
		int x;
		int y;
	} space[BOARD_SIZE];
	int space_len = 0, space_sel, x, y;
	for (y = 0; y < BOARD_H; y++){
		for (x = 0; x < BOARD_W; x++){
			if (0 == game->board[y][x]){
				space[space_len].x = x;
				space[space_len].y = y;
				space_len++;
			}
		}
	}
	space_sel = rand() % space_len;
	x = space[space_sel].x;
	y = space[space_sel].y;
	game->board[y][x] = (rand() % 2) ? 2 : 4;
	if (space_len > 1){
		return 1;
	}
	
	for (y = 0; y < BOARD_H; y++){
		for (x = 0; x < BOARD_W; x++){
			if (x < BOARD_W-1 && game->board[y][x] == game->board[y][x+1]){
				return 1;
			}
			if (y < BOARD_H-1 && game->board[y][x] == game->board[y+1][x]){
				return 1;
			}
		}
	}
	game->status = 2;
	return 2;
}
int game2048_move_up(game2048_t* g){
	int m = 0, x, y, x0, y0;
	for (x = 0; x < BOARD_W; x++){
		y0 = 0; y = 1;
		while (y < BOARD_H){
			if (0 == g->board[y0][x]){
				if (0 != g->board[y][x]){
					g->board[y0][x] = g->board[y][x];
					g->board[y][x] = 0;
					m = 1;
				}
				y++;
			} else {
				if (0 == g->board[y][x]){
					y++;
				} else if (g->board[y0][x] == g->board[y][x]) {
					g->score += (g->board[y][x] * 2);
					g->board[y0][x] <<= 1;
					g->board[y][x] = 0;
					y0++; y++;
					m = 1;
				} else {
					y0++;
					if (y0 == y) {
						y++;
					}
				}
			}
		}
	}
	if (m){
		return game2048_update(g);
	} else {
		return 0;
	}
}
int game2048_move_down(game2048_t* g){
	int m = 0, x, y, x0, y0;
	for (x = 0; x < BOARD_W; x++){
		y0 = BOARD_H - 1; y = BOARD_H - 2;
		while (y >= 0){
			if (0 == g->board[y0][x]){
				if (0 != g->board[y][x]){
					g->board[y0][x] = g->board[y][x];
					g->board[y][x] = 0;
					m = 1;
				}
				y--;
			} else {
				if (0 == g->board[y][x]){
					y--;
				} else if (g->board[y0][x] == g->board[y][x]) {
					g->score += (g->board[y][x] * 2);
					g->board[y0][x] <<= 1;
					g->board[y][x] = 0;
					y0--; y--;
					m = 1;
				} else {
					y0--;
					if (y0 == y) {
						y--;
					}
				}
			}
		}
	}
	if (m){
		return game2048_update(g);
	} else {
		return 0;
	}
}
int game2048_move_left(game2048_t* g){
	int m = 0, x, y, x0, y0;
	for (y = 0; y < BOARD_H; y++){
		x0 = 0; x = 1;
		while (x < BOARD_W){
			if (0 == g->board[y][x0]){
				if (0 != g->board[y][x]){
					g->board[y][x0] = g->board[y][x];
					g->board[y][x] = 0;
					m = 1;
				}
				x++;
			} else {
				if (0 == g->board[y][x]){
					x++;
				} else if (g->board[y][x0] == g->board[y][x]) {
					g->score += (g->board[y][x] * 2);
					g->board[y][x0] <<= 1;
					g->board[y][x] = 0;
					x0++; x++;
					m = 1;
				} else {
					x0++;
					if (x0 == x) {
						x++;
					}
				}
			}
		}
	}
	if (m){
		return game2048_update(g);
	} else {
		return 0;
	}
}
int game2048_move_right(game2048_t* g){
	int m = 0, x, y, x0, y0;
	for (y = 0; y < BOARD_H; y++){
		x0 = BOARD_W - 1; x = BOARD_W - 2;
		while (x >= 0){
			if (0 == g->board[y][x0]){
				if (0 != g->board[y][x]){
					g->board[y][x0] = g->board[y][x];
					g->board[y][x] = 0;
					m = 1;
				}
				x--;
			} else {
				if (0 == g->board[y][x]){
					x--;
				} else if (g->board[y][x0] == g->board[y][x]) {
					g->score += (g->board[y][x] * 2);
					g->board[y][x0] <<= 1;
					g->board[y][x] = 0;
					x0--; x--;
					m = 1;
				} else {
					x0--;
					if (x0 == x) {
						x--;
					}
				}
			}
		}
	}
	if (m){
		return game2048_update(g);
	} else {
		return 0;
	}
}

typedef enum _action_t{
	ACTION_NONE,
	ACTION_QUIT,
	ACTION_MOVE_UP,
	ACTION_MOVE_DOWN,
	ACTION_MOVE_LEFT,
	ACTION_MOVE_RIGHT,
}action_t;
action_t getaction(){
  unsigned int keyValue = 0;
  unsigned char ch = getch();
  if (ch && ch != 224){
    keyValue=ch;
  }else{
    keyValue=((unsigned int)getch())<<8;
  }
	switch (keyValue){
		case 0x1b:
			return ACTION_QUIT;
		break;
		case 0x4800:
			return ACTION_MOVE_UP;
		break;
		case 0x5000:
			return ACTION_MOVE_DOWN;
		break;
		case 0x4b00:
			return ACTION_MOVE_LEFT;
		break;
		case 0x4d00:
			return ACTION_MOVE_RIGHT;
		break;
	}
  return ACTION_NONE;
}
void main(){
	game2048_t game; int running = 1, moved;
	game2048_init(&game);

	initscr();
	drawframe();
	drawboard(&game);
	while (running && 0 == game.status){
		moved = 0;
		switch (getaction()){
			case ACTION_QUIT:
				running = 0;
			break;
			case ACTION_MOVE_UP:
				moved = game2048_move_up(&game);
			break;
			case ACTION_MOVE_DOWN:
				moved = game2048_move_down(&game);
			break;
			case ACTION_MOVE_LEFT:
				moved = game2048_move_left(&game);
			break;
			case ACTION_MOVE_RIGHT:
				moved = game2048_move_right(&game);
			break;
		}
		if (running && moved){
			drawboard(&game);
		}
	}
	if (game.status){
    sound(100);
    delay(100);
    nosound();
		while (ACTION_QUIT != getaction()){}
	}
	game2048_quit(&game);
	endscr();
}

