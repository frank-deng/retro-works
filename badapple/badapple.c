#include <stdio.h>
#include "keyboard.h"
#include "timer.h"
#include "video.h"
#include "frame.h"

static unsigned char frame_buffer[FRAME_WIDTH*FRAME_HEIGHT/64*10];

int main(){
    unsigned int curFrame=0;
    if(!initFrame()){
        return 1;
    }

    //Initialization
    initKeyboard();
    initTimer();
    initVideo();

    //Main loop
    while(0x01!=getKeypressed()){
        if(curFrame<getFrameCount()){
            getFrameData(frame_buffer,curFrame);
            curFrame++;
        }
        waitTimer();
    }

    //Clean up works
    closeVideo();
    closeTimer();
    closeKeyboard();
    closeFrame();

    return 0;
}
