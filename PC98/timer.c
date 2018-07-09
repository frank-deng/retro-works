#include <stdio.h>
#include <dos.h>
#include <conio.h>
#include <farstr.h>
#include <time.h>

#define	TMRMODE		0x77		/* timer mode port */
#define	TMR0MOD2	0x34		/* timer #0, mode 2(interval timer interrupt) */
#define	TMR0MOD3	0x36		/* timer #0, mode 3(square wave generator mode) */
#define	TMR1MOD0	0x70		/* timer #1, mode 0(interval timer mode) */
#define	TMR1MOD3	0x76		/* timer #1, mode 3(square wave generator mode) */

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

#define	SYSPORTC	0x35		/* system port C */
#define	BUZ_BIT		0x08		/* buzzer bit  0:on, 1:off */

#define	PICPORT		0x00		/* interrupt controller (int 08h = master) */
#define	EOI			0x20		/* end of interrupt */

static unsigned long tick = 0;
static void (far *OrgTimerVect)();
static unsigned char imr_m, imr_s;
static void NewTimerVectMain() {
	tick++;
	outp(PICPORT, EOI);
}
static void far NewTimerVect() {
	NewTimerVectMain();
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

static void enableTimer(){
	_asm_c("\n\tCLI\n");
	outp(IMR_M, inp(IMR_M)|TMRIMRBIT);
	_asm_c("\n\tSTI\n");

	OrgTimerVect = _dos_getvect(TMRINTVEC);
	_dos_setvect(TMRINTVEC, NewTimerVect);

	_asm_c("\n\tCLI\n");
	outp(IMR_M, inp(IMR_M)&(~TMRIMRBIT));
	outp(IMR_M, (imr_m = (unsigned char)inp(IMR_M))|(0x00));
	outp(IMR_S, (imr_s = (unsigned char)inp(IMR_S))|(0x20));
	_asm_c("\n\tSTI\n");
}
static void disableTimer(){
	_asm_c("\n\tCLI\n");
	outp(IMR_M, imr_m);
	outp(IMR_S, imr_s);
	outp(IMR_M, inp(IMR_M)|TMRIMRBIT);
	_asm_c("\n\tSTI\n");

	_dos_setvect(TMRINTVEC, OrgTimerVect);

	_asm_c("\n\tCLI\n");
	outp(IMR_M, inp(IMR_M)&(~TMRIMRBIT));
	_asm_c("\n\tSTI\n");
}
static unsigned int getOrigCounter(){
	outp(TMRMODE, TMR0MOD2);

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

	while (!origCounter) {
		_asm_c("\n\tHLT\n");
	}

	disableTimer();
	return origCounter;
}

void showTime(unsigned int secRemain){
	unsigned char min = secRemain / 60, sec = secRemain % 60;
	if (secRemain) {
		printf("\x0d< %02u:%02u >", min, sec);
	} else {
		printf("\x0d\033[41m< %02u:%02u >", min, sec);
	}
}
typedef enum _action_t{
	ACTION_NULL,
	ACTION_QUIT,
}action_t;
action_t getaction(){
	action_t action = ACTION_NULL;
	if (!kbhit()) {
		return action;
	}
	switch (getch()){
		case 0x1b:
			if (!kbhit()) {
				action = ACTION_QUIT;
			}
		break;
	}
	while(kbhit()){
		getch();
	}
	return action;
}
int main(){
	float minutes;
	unsigned int running = 1, counter, counter10ms, counterOrig;
	unsigned long maxticks;

	if (BIOS_FLAG&SYSCLK_BIT) {	/* 8MHz/16MHz... */
		counter = 998;
		counter10ms = 19968;
	} else {					/* 5MHz/10MHz... */
		counter = 1229;
		counter10ms = 24576;
	}

	printf("\033[2J");
	puts("\033[2;25H\033[21m*** カウントダウンタイマー ***\n\033[0m");
	printf("時間（分）：");
	scanf("%f", &minutes);
	puts("\nEscを押してシステムに戻ります\n");
	outp(0x62, 0x4b);
	outp(0x60, 0x0f);

	maxticks = (unsigned long)(minutes * 60.0 * 100);

	counterOrig = getOrigCounter();

	outp(TMRMODE, TMR1MOD3);
	outp(TMR1CLK, (int)(counter&0x00ff));
	outp(TMR1CLK, (int)(counter>>8));

	outp(TMRMODE, TMR0MOD2);
	outp(TMR0CLK, (int)(counter10ms&0x00ff));
	outp(TMR0CLK, (int)(counter10ms>>8));

	outp(SYSPORTC, (inp(SYSPORTC)|BUZ_BIT));

	enableTimer();
	while (running && tick < maxticks){
		_asm_c("\n\tHLT\n");
		if (0 == (tick & 0xF)) {
			disableTimer();
			showTime((maxticks - tick)/100);
			if (ACTION_QUIT == getaction()) {
				running = 0;
			}
			enableTimer();
		}
	}
	disableTimer();

	if (running){
		tick = 0;
		enableTimer();
		while (running){
			_asm_c("\n\tHLT\n");
			if (tick % 140 < 70) {
				outp(SYSPORTC, (inp(SYSPORTC)&(~BUZ_BIT)));
			} else {
				outp(SYSPORTC, (inp(SYSPORTC)|BUZ_BIT));
			}

			if (0 == (tick & 0xF)) {
				disableTimer();
				if (ACTION_QUIT == getaction()) {
					running = 0;
				}
				enableTimer();
			}
		}
		disableTimer();
	}

	outp(SYSPORTC, (inp(SYSPORTC)|BUZ_BIT));

	outp(TMRMODE, TMR0MOD3);
	outp(TMR0CLK, (int)(counterOrig&0x00ff));
	outp(TMR0CLK, (int)(counterOrig>>8));

	outp(0x62, 0x4b);
	outp(0x60, 0x8f);
	puts("\033[0m");
	return 0;
}

