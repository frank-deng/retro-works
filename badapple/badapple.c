#include <stdio.h>
#include <malloc.h>
#include "keyboard.h"
#include "timer.h"
#include "video.h"
#include "frame.h"

//#define _console_debug

static unsigned char frame_buffer[FRAME_WIDTH*FRAME_HEIGHT/8+FRAME_WIDTH*FRAME_HEIGHT/64*2];

int main(){
    unsigned int curFrame=0, frameDataLen=0;
    //Initialization
    if(!initFrame()){
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
    while(0x01!=getKeypressed()){
        if(curFrame<getFrameCount()){
            frameDataLen=getFrameData(frame_buffer,curFrame);
            drawFrame(frame_buffer,frameDataLen);
            curFrame++;
        }
        waitTimer();
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
