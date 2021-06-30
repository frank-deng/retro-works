#include <stdio.h>
#include <malloc.h>
#include <io.h>
#include "keyboard.h"
#include "timer.h"
#include "video.h"
#include "wav.h"

//#define _console_debug
char* getWavFile(){
    if(!access("badapple.wav",R_OK)){
        return "badapple.wav";
    }
    if(!access("B:\\badapple.wav",R_OK)){
        return "B:\\badapple.wav";
    }
    return NULL;
}
int main(){
    unsigned int stuck=0;
    unsigned char hasNextFrame=1;
    frame_t *frame;
    wav_t *wav=NULL;
    char *wavFilePath=NULL;

    //Initialization
    puts("Loading...");
    frame=initFrame();
    if(NULL==frame){
        return 1;
    }
    wavFilePath=getWavFile();
    if(NULL==wavFilePath){
        perror("Unable to find music WAV file badapple.wav or B:\\badapple.wav");
        return 1;
    }
    wav=openWAV(wavFilePath);
    if(NULL==wav){
        closeFrame();
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
            if(frame->bufferLength){
                drawFrame(frame);
            }
            hasNextFrame=loadNextFrame(frame);
            if(hasNextFrame){
                readWAVBuffer(wav);
            }else{
                soundOff();
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
