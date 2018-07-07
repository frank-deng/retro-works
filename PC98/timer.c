#include <stdio.h>
#include <dos.h>
#include <conio.h>
#include <farstr.h>
#include <time.h>

typedef enum _action_t{
	ACTION_QUIT,
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
	}
}

static void setfreq(unsigned int timer, unsigned int freq){
#define	TMR0CLK		0x71		/* timer #0 counter set port */
#define	TMR1CLK		0x3fdb		/* timer #1 counter set port */
#define	BIOS_FLAG	*(unsigned char far *)0x00000501L	/* BIOS_FLAG at system area */
#define	SYSCLK_BIT	0x80		/* system clock bit  0:5/10/20MHz, 1:8/16MHz */
#define	COUNT5		2457600L	/* timer clock freq.[Hz] at 5/10/20MHz */
#define	COUNT8		1996800L	/* timer clock freq.[Hz] at 8/16MHz */
	unsigned int count;
	if (BIOS_FLAG&SYSCLK_BIT) {				/* 8MHz/16MHz... */
		count = (unsigned int)((double)COUNT8/(double)freq+0.5);
	}
	else {									/* 5MHz/10MHz... */
		count = (unsigned int)((double)COUNT5/(double)freq+0.5);
	}
	if (timer) {
		outp(TMR1CLK, (int)(count&0x00ff));		/* rate LSB */
		outp(TMR1CLK, (int)(count>>8));			/* rate MSB */
	} else {
		outp(TMR0CLK, (int)(count&0x00ff));		/* rate LSB */
		outp(TMR0CLK, (int)(count>>8));			/* rate MSB */
	}
}

static void set10msec(unsigned int timer){
#define	TMR0CLK		0x71		/* timer #0 counter set port */
#define	TMR1CLK		0x3fdb		/* timer #1 counter set port */
#define	BIOS_FLAG	*(unsigned char far *)0x00000501L	/* BIOS_FLAG at system area */
#define	SYSCLK_BIT	0x80		/* system clock bit  0:5/10/20MHz, 1:8/16MHz */
#define	COUNT5		2457600L	/* timer clock freq.[Hz] at 5/10/20MHz */
#define	COUNT8		1996800L	/* timer clock freq.[Hz] at 8/16MHz */
	unsigned int count;
	if (BIOS_FLAG&SYSCLK_BIT) {
		count = 19968;
	} else {
		count = 24576;
	}
	if (timer) {
		outp(TMR1CLK, (int)(count&0x00ff));		/* rate LSB */
		outp(TMR1CLK, (int)(count>>8));			/* rate MSB */
	} else {
		outp(TMR0CLK, (int)(count&0x00ff));		/* rate LSB */
		outp(TMR0CLK, (int)(count>>8));			/* rate MSB */
	}
}

static void far *OrgTimerVect;
static long num = 0x3FFFFF;
static int k = 0;

#define	IMR_M		0x02		/* IMR r/w port(master) */
#define	TMRIMRBIT	0x01		/* timer IRQ mask bit */
#define	IMR_S		0x0a		/* IMR r/w port(slave) */
#define	TMRINTVEC	0x08		/* timer interrupt vector number */

#define	TMRMODE		0x77		/* timer mode port */
#define	TMR0MOD2	0x34		/* timer #0, mode 0(interval timer mode) */
#define	TMR1MOD0	0x70		/* timer #1, mode 0(interval timer mode) */
#define	TMR1MOD3	0x76		/* timer #1, mode 3(square wave generator mode) */

#define	SYSPORTC	0x35		/* system port C */
#define	BUZ_BIT		0x08		/* buzzer bit  0:on, 1:off */

static void NewTimerVectMain() {
#define	PICPORT		0x00		/* interrupt controller (int 08h = master) */
#define	EOI			0x20		/* end of interrupt */
	k++;
	outp(PICPORT, EOI);
}
static void far NewTimerVect() {
	NewTimerVectMain();
	_asm_c("\n\tIRET\n");
}
int main(){
	unsigned char imr_m, imr_s, tmr0mod;

	_asm_c("\n\tCLI\n");
	outp(IMR_M, inp(IMR_M)|TMRIMRBIT);
	_asm_c("\n\tSTI\n");

	tmr0mod = inp(TMRMODE);
	outp(TMRMODE, TMR0MOD2);
	set10msec(0);

	outp(TMRMODE, TMR1MOD3);
	setfreq(1, 200);
	outp(SYSPORTC, (inp(SYSPORTC)&(~BUZ_BIT)));

	OrgTimerVect = _dos_getvect(TMRINTVEC);
	_dos_setvect(TMRINTVEC, NewTimerVect);

	_asm_c("\n\tCLI\n");
	outp(IMR_M, inp(IMR_M)&(~TMRIMRBIT));
	outp(IMR_M, (imr_m = (unsigned char)inp(IMR_M))|(0x00));
	outp(IMR_S, (imr_s = (unsigned char)inp(IMR_S))|(0x20));
	_asm_c("\n\tSTI\n");

	while (k < 600){
		_asm_c("\n\tHLT\n");
	}

	_asm_c("\n\tCLI\n");
	outp(IMR_M, imr_m);
	outp(IMR_S, imr_s);
	outp(IMR_M, inp(IMR_M)|TMRIMRBIT);
	_asm_c("\n\tSTI\n");

	outp(SYSPORTC, (inp(SYSPORTC)|BUZ_BIT));
	outp(TMRMODE, tmr0mod);
	setfreq(0, 2000);
	outp(TMRMODE, TMR1MOD3);
	setfreq(1, 2000);
	_dos_setvect(TMRINTVEC, OrgTimerVect);

	_asm_c("\n\tCLI\n");
	outp(IMR_M, inp(IMR_M)&(~TMRIMRBIT));
	_asm_c("\n\tSTI\n");

	printf("%d %d", k, num);

	return 0;
}

