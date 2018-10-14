#include <dos.h>

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
void (interrupt far *OrgTimerVect)();
static void interrupt far NewTimerVect() {
	tick++;
	(OrgTimerVect)();
}

static unsigned int origCounter = 0;
static void interrupt far GetTimerVect() {
	unsigned char lo, hi;
	lo = inp(TMR0CLK);
	hi = inp(TMR0CLK);
	origCounter = hi;
	origCounter <<= 8;
	origCounter |= lo;
	(OrgTimerVect)();
}

int main(){
	unsigned int count;
	unsigned char imr_m, imr_s;

	if (BIOS_FLAG&SYSCLK_BIT) {	/* 8MHz/16MHz... */
		count = 998;
	} else {					/* 5MHz/10MHz... */
		count = 1229;
	}

	outp(TMRMODE, TMR0MOD2);

	/* Enable Timer */
	asm { CLI }
	outp(IMR_M, inp(IMR_M)|TMRIMRBIT);
	asm { STI }

	OrgTimerVect = getvect(TMRINTVEC);
	setvect(TMRINTVEC, GetTimerVect);

	asm { CLI }
	outp(IMR_M, inp(IMR_M)&(~TMRIMRBIT));
	outp(IMR_M, (imr_m = (unsigned char)inp(IMR_M))|(0x00));
	outp(IMR_S, (imr_s = (unsigned char)inp(IMR_S))|(0x20));
	asm { STI }
	/* Enable Timer Finishend */

	/* Get clock */
	while (!origCounter) {
		asm { HLT }
	}
	outp(TMR0CLK, (int)(count&0x00ff));
	outp(TMR0CLK, (int)(count>>8));
	/* Get clock end */

	/* Change Timer */
	asm { CLI }
	outp(IMR_M, inp(IMR_M)|TMRIMRBIT);
	asm { STI }

	setvect(TMRINTVEC, NewTimerVect);

	asm { CLI }
	outp(IMR_M, inp(IMR_M)&(~TMRIMRBIT));
	asm { STI }
	/* Change Timer Finishend */

	/* Play beep sound */
	outp(TMRMODE, TMR1MOD3);
	outp(TMR1CLK, (int)(count&0x00ff));
	outp(TMR1CLK, (int)(count>>8));
	outp(SYSPORTC, (inp(SYSPORTC)&(~BUZ_BIT)));
	while (tick <= 15){
		asm { HLT }
	}
	outp(TMR1CLK, (int)((count << 1)&0x00ff));
	outp(TMR1CLK, (int)((count << 1)>>8));
	while (tick <= 30){
		asm { HLT }
	}
	outp(SYSPORTC, (inp(SYSPORTC)|BUZ_BIT));
	outp(TMR1CLK, (int)(count&0x00ff));
	outp(TMR1CLK, (int)(count>>8));
	/* Play beep sound end */

	/* Disable Timer */
	asm { CLI }
	outp(IMR_M, imr_m);
	outp(IMR_S, imr_s);
	outp(IMR_M, inp(IMR_M)|TMRIMRBIT);
	asm { STI }

	setvect(TMRINTVEC, OrgTimerVect);

	asm { CLI }
	outp(IMR_M, inp(IMR_M)&(~TMRIMRBIT));
	asm { STI }
	/* Disable Timer Finishend */

	outp(TMRMODE, TMR0MOD2);
	outp(TMR0CLK, (int)(origCounter&0x00ff));
	outp(TMR0CLK, (int)(origCounter>>8));
	return 0;
}

