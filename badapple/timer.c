#include <dos.h>
#include <conio.h>
#include "timer.h"

static void __inline hlt();
#pragma aux hlt = "hlt";
static __inline void cli();
#pragma aux cli = "cli";
static __inline void sti();
#pragma aux sti = "sti";

static void (__interrupt __far * timerHandlerOrig)();
static wav_t *wavInstance;
static unsigned int timerCycles=0;
void __interrupt timerHandler(){
    uint16_t sampleValue;
    cli();
    timerCycles++;
    sampleValue=getSample(wavInstance);
    outp(0x43,0x96);
    outp(0x42,((sampleValue*64/255)&0xff));
    outp(0x20,0x20);
    sti();
    //(*timerHandlerOrig)();
}
void initTimer(wav_t *wav){
    wavInstance=wav;
    timerHandlerOrig=_dos_getvect(0x08);
    _dos_setvect(0x08,timerHandler);
	outp(0x43,0x34);
    outp(0x40,0x23);
    outp(0x40,0x1);
    soundOn();
    /*
    outp(0x40,0xa7);
    outp(0x40,0x91);
    */
}
void closeTimer(){
    soundOff();
    _dos_setvect(0x08,timerHandlerOrig);
	outp(0x43,0x34);
    outp(0x40,0xff);
    outp(0x40,0xff);
}
void soundOn(){
    outp(0x61,inp(0x61)|0x3); //Enable speaker
}
void soundOff(){
    outp(0x61,inp(0x61)&(~0x3)); //Disable speaker
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
