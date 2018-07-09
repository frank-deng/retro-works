#include <stdio.h>
#include <dos.h>
#include <conio.h>
#include <farstr.h>
#include <stdlib.h>
#include <time.h>
#include <jctype.h>

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
static uint16_t far* vram = 0xA0000000;
static uint16_t far* vramattr = 0xA0002000;

void clrscr();
void initscr(){
	putchar('\x1e');
	inregs.x.dx = 0;
	inregs.h.ah = 0x13;
	int86y(0x18, &inregs, &outregs);
	outp(0x62, 0x4b);
	outp(0x60, 0x0f);
	clrscr();
}
void endscr(){
	clrscr();
	outp(0x62, 0x4b);
	outp(0x60, 0x8f);
	putchar('\x1e');
	printf("\033[2J");
}
void clrscr(){
	far_memset((void far *)vram, 0, 4000);
	far_memset((void far *)vramattr, 0, 4000);
}
void cputchar(uint16_t ch, uint16_t x, uint16_t y, uint16_t attr){
	uint16_t offset = (y<<6) + (y<<4) + x;
	uint16_t far *p_vram = (uint16_t far*)(vram + offset);
	uint16_t far *p_vramattr = (uint16_t far*)(vramattr + offset);
	
	if (ch > 0xFF){
		*p_vram = ch - 0x20;
		*(p_vram + 1) = ch + 0x60;
		*(p_vramattr) = attr;
		*(p_vramattr + 1) = attr;
	} else {
		*p_vram = ch;
		*p_vramattr = attr;
	}
}
void cputstr(char* str, uint16_t x, uint16_t y, uint16_t attr){
	uint16_t offset = (y<<6) + (y<<4) + x;
	uint16_t far *p_vram = (uint16_t far*)(vram + offset);
	uint16_t far *p_vramattr = (uint16_t far*)(vramattr + offset);
	char *ch;
				
	for (ch = str; *ch != '\0'; ch++){
		*p_vram = (uint16_t)(*ch);
		*p_vramattr = attr;
		p_vram++;
		p_vramattr++;
	}
}
void cputstrj(char* str, uint16_t x, uint16_t y, uint16_t attr){
	char *p;
	uint16_t offset = (y<<6) + (y<<4) + x;
	uint16_t far *p_vram = (uint16_t far*)(vram + offset);
	uint16_t far *p_vramattr = (uint16_t far*)(vramattr + offset);
	unsigned short ch, ch2;
	
	for (p = str; *p != '\0'; p++, p_vram++, p_vramattr++){
		ch = *p; ch <<= 8; ch |= *(p+1);
		if (jiszen(ch)) {
			ch2 = jmstojis(ch);
			ch = (ch2 << 8) | (0xFF & (ch2 >> 8));
			*p_vram = ch - 0x20;
			*p_vramattr = attr;
			p++;
			p_vram++;
			p_vramattr++;
			*p_vram = ch + 0x60;
			*p_vramattr = attr;
		} else {
			*p_vram = (uint16_t)(*p);
			*p_vramattr = attr;
		}
	}
}
void drawframe(){
	int i;
	cputstrj("得点：", 28, 5, 0xc1);

#define ATTR_BORDER 0x21
	cputchar('\x9c', 27, 7, ATTR_BORDER);
	for (i = 0; i < 24; i++){
		cputchar('\x95', 28+i, 7, ATTR_BORDER);
	}
	cputchar('\x9d', 27+25, 7, ATTR_BORDER);

	for (i = 0; i < 9; i++){
		cputchar('\x96', 27, 8+i, ATTR_BORDER);
		cputchar('\x96', 27+25, 8+i, ATTR_BORDER);
	}

	cputchar('\x9e', 27, 17, ATTR_BORDER);
	for (i = 0; i < 24; i++){
		cputchar('\x95', 28+i, 17, ATTR_BORDER);
	}
	cputchar('\x9f', 27+25, 17, ATTR_BORDER);
}
void drawboard(game2048_t* game){
	int x, y;
	char buf[16] = {'\0'};
	for (y = 0; y < BOARD_H; y++){
		for (x = 0; x < BOARD_W; x++){
			if (game->board[y][x]) {
				sprintf(buf, "%5u ", game->board[y][x]);
				cputstr(buf, 28+6*x, 9+(y<<1), 0xe1);
			} else {
				cputstr("    . ", 28+6*x, 9+(y<<1), 0xe1);
			}
		}
	}
	sprintf(buf, "%lu", game->score);
	cputstr(buf, 34, 5, 0xc1);
	if (game->status){
		cputstrj("ゲームオーバー", 33, 19, 0x41);
	}
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
	game2048_update(game);
}
void game2048_quit(game2048_t* game){
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

/* Functions for beep and timer */
#define	TMR0CLK		0x71		/* timer #0 counter set port */
#define	TMR1CLK		0x3fdb		/* timer #1 counter set port */
#define	BIOS_FLAG	*(unsigned char far *)0x00000501L	/* BIOS_FLAG at system area */
#define	SYSCLK_BIT	0x80		/* system clock bit  0:5/10/20MHz, 1:8/16MHz */
#define	COUNT5		2457600L	/* timer clock freq.[Hz] at 5/10/20MHz */
#define	COUNT8		1996800L	/* timer clock freq.[Hz] at 8/16MHz */

#define	IMR_M		0x02		/* IMR r/w port(master) */
#define	TMRIMRBIT	0x01		/* timer IRQ mask bit */
#define	IMR_S		0x0a		/* IMR r/w port(slave) */
#define	TMRINTVEC	0x08		/* timer interrupt vector number */

#define	TMRMODE		0x77		/* timer mode port */
#define	TMR0MOD2	0x34		/* timer #0, mode 2(timer mode) */
#define	TMR1MOD0	0x70		/* timer #1, mode 0(interval timer mode) */
#define	TMR1MOD3	0x76		/* timer #1, mode 3(square wave generator mode) */

#define	SYSPORTC	0x35		/* system port C */
#define	BUZ_BIT		0x08		/* buzzer bit  0:on, 1:off */

#define	PICPORT		0x00		/* interrupt controller (int 08h = master) */
#define	EOI			0x20		/* end of interrupt */

static unsigned long tick = 0;
static void NewTimer() {
	tick++;
	outp(PICPORT, EOI);
}
static void far NewTimerVect() {
	NewTimer();
	_asm_c("\n\tIRET\n");
}

static unsigned int origCounter = 0;
static void GetTimer() {
	unsigned char lo, hi;
	lo = inp(TMR0CLK);
	hi = inp(TMR0CLK);
	origCounter = hi;
	origCounter <<= 8;
	origCounter |= lo;
	outp(PICPORT, EOI);
}
static void far GetTimerVect() {
	GetTimer();
	_asm_c("\n\tIRET\n");
}
static void beep(unsigned int freq){
	unsigned int count;
	void (far *OrgTimerVect)();
	unsigned char imr_m, imr_s;

	outp(TMRMODE, TMR0MOD2);

	/* Enable Timer */
	_asm_c("\n\tCLI\n");
	outp(IMR_M, inp(IMR_M)|TMRIMRBIT);
	_asm_c("\n\tSTI\n");

	OrgTimerVect = _dos_getvect(TMRINTVEC);
	_dos_setvect(TMRINTVEC, GetTimerVect);

	_asm_c("\n\tCLI\n");
	outp(IMR_M, inp(IMR_M)&(~TMRIMRBIT));
	outp(IMR_M, (imr_m = (unsigned char)inp(IMR_M))|(0x00));
	outp(IMR_S, (imr_s = (unsigned char)inp(IMR_S))|(0x20));
	_asm_c("\n\tSTI\n");
	/* Enable Timer Finishend */

	/* Get clock */
	while (!origCounter) {
		_asm_c("\n\tHLT\n");
	}
	if (BIOS_FLAG&SYSCLK_BIT) {	/* 8MHz/16MHz... */
		count = 19968;
	} else {					/* 5MHz/10MHz... */
		count = 24576;
	}
	outp(TMR0CLK, (int)(count&0x00ff));
	outp(TMR0CLK, (int)(count>>8));
	/* Get clock end */

	/* Switch Timer */
	_asm_c("\n\tCLI\n");
	outp(IMR_M, inp(IMR_M)|TMRIMRBIT);
	_asm_c("\n\tSTI\n");

	_dos_setvect(TMRINTVEC, NewTimerVect);

	_asm_c("\n\tCLI\n");
	outp(IMR_M, inp(IMR_M)&(~TMRIMRBIT));
	_asm_c("\n\tSTI\n");
	/* Enable Timer Finishend */

	/* Play beep sound */
	outp(TMRMODE, TMR1MOD3);
	if (BIOS_FLAG&SYSCLK_BIT) {	/* 8MHz/16MHz... */
		count = 19968;
	} else {					/* 5MHz/10MHz... */
		count = 24576;
	}
	outp(TMR1CLK, (int)(count&0x00ff));
	outp(TMR1CLK, (int)(count>>8));
	outp(SYSPORTC, (inp(SYSPORTC)&(~BUZ_BIT)));
	while (tick <= 15){
		_asm_c("\n\tHLT\n");
	}
	outp(SYSPORTC, (inp(SYSPORTC)|BUZ_BIT));
	if (BIOS_FLAG&SYSCLK_BIT) {	/* 8MHz/16MHz... */
		count = 998;
	} else {					/* 5MHz/10MHz... */
		count = 1229;
	}
	outp(TMR1CLK, (int)(count&0x00ff));
	outp(TMR1CLK, (int)(count>>8));
	/* Play beep sound end */

	/* Disable Timer */
	_asm_c("\n\tCLI\n");
	outp(IMR_M, imr_m);
	outp(IMR_S, imr_s);
	outp(IMR_M, inp(IMR_M)|TMRIMRBIT);
	_asm_c("\n\tSTI\n");

	_dos_setvect(TMRINTVEC, OrgTimerVect);

	_asm_c("\n\tCLI\n");
	outp(IMR_M, inp(IMR_M)&(~TMRIMRBIT));
	_asm_c("\n\tSTI\n");
	/* Disable Timer Finishend */

	outp(TMRMODE, TMR0MOD2);
	outp(TMR0CLK, (int)(origCounter&0x00ff));
	outp(TMR0CLK, (int)(origCounter>>8));
}

typedef enum _action_t{
	ACTION_QUIT,
	ACTION_MOVE_UP,
	ACTION_MOVE_DOWN,
	ACTION_MOVE_LEFT,
	ACTION_MOVE_RIGHT,
}action_t;
action_t getaction(){
	char ch;
	ch = getch();
	switch (ch){
		case 0x1b:
			if (!kbhit()) {
				return ACTION_QUIT;
			}
		break;
		case 0x0b:
			return ACTION_MOVE_UP;
		break;
		case 0x0a:
			return ACTION_MOVE_DOWN;
		break;
		case 0x08:
			return ACTION_MOVE_LEFT;
		break;
		case 0x0c:
			return ACTION_MOVE_RIGHT;
		break;
	}
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
		beep(100);
		while (ACTION_QUIT != getaction()){}
	}
	game2048_quit(&game);
	endscr();
}

