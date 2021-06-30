#include <dos.h>
#include <conio.h>
#include "timer.h"

static __inline void hlt();
#pragma aux hlt = "hlt";
static __inline void cli();
#pragma aux cli = "cli";
static __inline void sti();
#pragma aux sti = "sti";

uint8_t wavFreqTable[]={
    0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,8,8,8,8,8,9,9,9,9,10,10,10,10,11,
    11,11,11,12,12,12,12,12,13,13,13,13,14,14,14,14,15,15,15,15,16,16,16,16,16,17,17,17,17,18,18,18,18,
    19,19,19,19,20,20,20,20,20,21,21,21,21,22,22,22,22,23,23,23,23,24,24,24,24,24,25,25,25,25,26,26,26,26,
    27,27,27,27,28,28,28,28,28,29,29,29,29,30,30,30,30,31,31,31,31,32,32,32,32,32,33,33,33,33,34,34,34,34,
    35,35,35,35,36,36,36,36,36,37,37,37,37,38,38,38,38,39,39,39,39,40,40,40,40,40,41,41,41,41,42,42,42,42,43,
    43,43,43,44,44,44,44,44,45,45,45,45,46,46,46,46,47,47,47,47,48,48,48,48,48,49,49,49,49,50,50,50,50,51,51,
    51,51,52,52,52,52,52,53,53,53,53,54,54,54,54,55,55,55,55,56,56,56,56,56,57,57,57,57,58,58,58,58,59,59,59,
    59,60,60,60
};

static __inline void setSpeakerFreq(uint8_t value);
#pragma aux setSpeakerFreq=\
    "mov al,0x96"\
    "out 0x43,al"\
    "mov al,ah"\
    "out 0x42,al"\
    "sti"\
    "mov al,0x20"\
    "out 0x20,al"\
    modify [ax]\
    parm [ah];

static void (__interrupt __far * timerHandlerOrig)();
static wav_t *wavInstance;
static audio_buffer_t *audio_buffer;
static unsigned int timerCycles=0;
void __interrupt timerHandler(){
    static uint8_t sampleValue;
    uint16_t offset;

    cli();
    timerCycles++;
    offset=audio_buffer->offset;
    if(offset < audio_buffer->length){
        sampleValue=audio_buffer->data[offset];
        audio_buffer->offset++;
    }
    setSpeakerFreq(wavFreqTable[sampleValue]);
    //(*timerHandlerOrig)();
}
void initTimer(wav_t *wav){
    wavInstance=wav;
    timerUpdateBuffer();
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
	outp(0x43,0xb6);
    outp(0x42,0xff);
    outp(0x42,0x3);
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
void timerUpdateBuffer(){
    audio_buffer=wavInstance->audioBufferUse;
}
