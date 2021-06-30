#ifndef __frame_h__
#define __frame_h__

#include <stdio.h>
#include <io.h>
typedef unsigned char uint8_t;
//typedef unsigned int uint16_t;
typedef struct{
    FILE *fp;
    uint16_t frameCount;
    uint16_t currentFrame;
    uint16_t* frameLenArr;
    uint16_t bufferLength;
    uint8_t *buffer;
}frame_t;

frame_t* initFrame();
void closeFrame();
unsigned char loadNextFrame(frame_t *frame);

#endif
