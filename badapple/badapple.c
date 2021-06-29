#include <stdio.h>
#include <malloc.h>
#include "keyboard.h"
#include "timer.h"
#include "video.h"

//#define _console_debug

int main(){
    unsigned int stuck=0;
    unsigned char hasNextFrame=1;
    frame_t *frame;
    //Initialization
    puts("Loading...");
    frame=initFrame();
    if(NULL==frame){
        return 1;
    }
#ifndef _console_debug
    initKeyboard();
    initTimer();
    initVideo();
#endif

    //Main loop
#ifdef _console_debug
    dumpData(frame_buffer,frameDataLen);
#endif
#ifndef _console_debug
    waitTimer(1);
    while(0x01!=getKeypressed()){
        if(hasNextFrame){
            drawFrame(frame);
            hasNextFrame=loadNextFrame();
        }
        stuck=waitTimer(4);
        if(stuck){
            printf("%d\n",stuck);
        }
    }
#endif

    //Clean up works
#ifndef _console_debug
    closeVideo();
    closeTimer();
    closeKeyboard();
#endif
    closeFrame();

    return 0;
}
