#include <stdio.h>
#include <malloc.h>
#include "keyboard.h"
#include "timer.h"
#include "video.h"
#include "wav.h"

//#define _console_debug

int main(){
    unsigned int stuck=0;
    unsigned char hasNextFrame=1;
    frame_t *frame;
    wav_t *wav=NULL;

    //Initialization
    puts("Loading...");
    frame=initFrame();
    if(NULL==frame){
        return 1;
    }
    wav=openWAV("B:\\badapple.wav");
    if(NULL==wav){
        return 1;
    }
#ifndef _console_debug
    initKeyboard();
    initTimer(wav);
    initVideo();
#endif

    //Main loop
#ifdef _console_debug
    dumpData(frame_buffer,frameDataLen);
#endif
#ifndef _console_debug
    while(0x01!=getKeypressed()){
        if(hasNextFrame){
            switchWAVBuffer(wav);
            drawFrame(frame);
            hasNextFrame=loadNextFrame();
            if(hasNextFrame){
                readWAVBuffer(wav);
            }
        }
        waitTimer(512);
        /*
        stuck=waitTimer(512);
        if(stuck){
            printf("%d\n",stuck);
        }
        */
    }
#endif

    //Clean up works
#ifndef _console_debug
    closeWAV(wav);
    closeVideo();
    closeTimer();
    closeKeyboard();
#endif
    closeFrame();

    return 0;
}
