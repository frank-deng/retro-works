#include <dos.h>

#define	TMRMODE		0x77		/* timer mode port */
#define	TMR1MOD0	0x70		/* timer #1, mode 0(interval timer mode) */
#define	TMR1MOD3	0x76		/* timer #1, mode 3(square wave generator mode) */
#define	TMR1CLK		0x3fdb		/* timer #1 counter set port */
#define	BIOS_FLAG	*(unsigned char far *)0x00000501L	/* BIOS_FLAG at system area */
#define	SYSCLK_BIT	0x80		/* system clock bit  0:5/10/20MHz, 1:8/16MHz */
#define	SYSPORTC	0x35		/* system port C */
#define	BUZ_BIT		0x08		/* buzzer bit  0:on, 1:off */

int main(){
  unsigned int counter;
	if (BIOS_FLAG&SYSCLK_BIT){
		counter = 998;
	} else {
		counter = 1229;
	}

	outp(TMRMODE, TMR1MOD3);
	outp(TMR1CLK, (int)(counter&0x00ff));
	outp(TMR1CLK, (int)(counter>>8));
	outp(SYSPORTC, (inp(SYSPORTC)&(~BUZ_BIT)));
  delay(150);
  counter<<=1;
	outp(TMR1CLK, (int)(counter&0x00ff));
	outp(TMR1CLK, (int)(counter>>8));
  delay(150);
	outp(SYSPORTC, (inp(SYSPORTC)|BUZ_BIT));

  return 0;
}

