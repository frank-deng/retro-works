#include <dos.h>
#include <conio.h>
#include "timer.h"

void hlt();
#pragma aux hlt = "hlt";

static void (__interrupt __far * timerHandlerOrig)();
static unsigned long timerCycles=0;
void __interrupt timerHandler(){
    timerCycles++;
    (*timerHandlerOrig)();
}
void initTimer(){
    timerHandlerOrig=_dos_getvect(0x08);
    _dos_setvect(0x08,timerHandler);
	outp(0x43,0x52);
    outp(0x40,0xa7);
    outp(0x40,0x91);
}
void closeTimer(){
    _dos_setvect(0x08,timerHandlerOrig);
	outp(0x43,0x52);
    outp(0x40,0xff);
    outp(0x40,0xff);
}
int waitTimer(unsigned int cycles){
    unsigned int stuckCycles=0;
    while(timerCycles<cycles){
        hlt();
    }
    if(timerCycles>cycles){
        stuckCycles=timerCycles-cycles;
    }
    timerCycles=0;
    return stuckCycles;
}
