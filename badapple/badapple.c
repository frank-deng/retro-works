#include <stdio.h>
#include "keyboard.h"
#include "timer.h"
#include "video.h"
#include "frame.h"

static unsigned char frame_buffer[FRAME_WIDTH*FRAME_HEIGHT/64*10];
static unsigned char block0[8]={0x55,0xaa,0x55,0xaa,0x55,0xaa,0x55,0xaa};
static unsigned char block1[8]={0xff,0x81,0x81,0x81,0x81,0x81,0x81,0xff};

int main(){
    unsigned int curFrame=0, frameDataLen=0;
    if(!initFrame()){
        return 1;
    }

    //Initialization
    //initKeyboard();
    //initTimer();
    //initVideo();

    //Main loop
    frameDataLen=getFrameData(frame_buffer,13);
    printf("%x %x",frame_buffer[0],frame_buffer[1]);
    //drawFrame(frame_buffer,frameDataLen);
    /*
    while(0x01!=getKeypressed()){
        waitTimer();
    }
    */

    //Clean up works
    /*
    closeVideo();
    closeTimer();
    closeKeyboard();
    */
    closeFrame();

    return 0;
}
