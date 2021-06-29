#include <dos.h>
#include <conio.h>
#include "timer.h"

static void __inline hlt();
#pragma aux hlt = "hlt";

static void (__interrupt __far * timerHandlerOrig)();
static wav_t *wavInstance;
static unsigned int timerCycles=0;
void __interrupt timerHandler(){
    uint16_t sampleValue;
    timerCycles++;
    sampleValue=getSample(wavInstance);
    outp(0x43,0x96);
    outp(0x42,((sampleValue*64/255)&0xff));
    outp(0x20,0x20);
    //(*timerHandlerOrig)();
}
void initTimer(wav_t *wav){
    wavInstance=wav;
    timerHandlerOrig=_dos_getvect(0x08);
    _dos_setvect(0x08,timerHandler);
	outp(0x43,0x34);
    outp(0x40,0x23);
    outp(0x40,0x1);
    outp(0x61,inp(0x61)|0x3); //Enable speaker
    /*
    outp(0x40,0xa7);
    outp(0x40,0x91);
    */
}
void closeTimer(){
    outp(0x61,inp(0x61)&(~0x3)); //Disable speaker
    _dos_setvect(0x08,timerHandlerOrig);
	outp(0x43,0x34);
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
