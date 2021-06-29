#ifndef __frame_h__
#define __frame_h__

#define FRAME_WIDTH 160
#define FRAME_HEIGHT 104

typedef struct{
    unsigned int length;
    unsigned char *data;
}frame_t;

frame_t* initFrame();
void closeFrame();
unsigned char loadNextFrame();

#endif
