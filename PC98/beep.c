#include <stdio.h>
#include <dos.h>
#include <conio.h>
#include <farstr.h>
#include <time.h>

#define	PICPORT		0x00		/* interrupt controller (int 08h = master) */
#define	EOI			0x20		/* end of interrupt */
#define	IMR_M		0x02		/* IMR r/w port(master) */
#define	TMRIMRBIT	0x01		/* timer IRQ mask bit */
#define	RS2IMRBIT	0x10		/* rs-232c IRQ mask bit */
#define	IMR_S		0x0a		/* IMR r/w port(slave) */
#define	MOSIMRBIT	0x20		/* mouse IRQ mask bit */
#define	TMRINTVEC	0x08		/* timer interrupt vector number */

#define	TMRMODE		0x77		/* timer mode port */
#define	TMR0MOD3	0x36		/* timer #0, mode 3(square) */
#define	TMR1MOD0	0x70		/* timer #1, mode 0(interval timer mode) */
#define	TMR1MOD3	0x76		/* timer #1, mode 3(square wave generator mode) */

#define	TMR0CLK		0x71		/* timer #0 counter set port */
#define	TMR1CLK		0x3fdb		/* timer #1 counter set port */

#define	SYSPORTC	0x35		/* system port C */
#define	BUZ_BIT		0x08		/* buzzer bit  0:on, 1:off */

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

static unsigned int	count;
static void setfreq(unsigned int timer, unsigned int freq){
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
	outp(timer, (int)(count&0x00ff));		/* rate LSB */
	outp(timer, (int)(count>>8));			/* rate MSB */
}
int main(){
	setfreq(TMR1CLK, 1000);

	outp(TMRMODE, TMR1MOD3);				/* counter mode 3 */
	outp(SYSPORTC, (inp(SYSPORTC)&(~BUZ_BIT)));	/* beep on */

	while (ACTION_QUIT != getaction()){
	}
	setfreq(TMR1CLK, 2000);
	while (ACTION_QUIT != getaction()){
	}
	outp(SYSPORTC, (inp(SYSPORTC)|BUZ_BIT));		/* beep off */

	return 0;
}

