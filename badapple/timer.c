#include <dos.h>
#include <conio.h>
#include "timer.h"

void hlt();
#pragma aux hlt = "hlt";

static void (__interrupt __far * timerHandlerOrig)();
static unsigned char waitFlag=1;
void __interrupt timerHandler(){
    waitFlag=0;
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
unsigned char waitTimer(unsigned int cycles){
    unsigned char stuck=1;
    while(waitFlag){
        stuck=0;
        hlt();
    }
    waitFlag=0;
    return stuck;
}
