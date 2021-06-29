#ifndef __frame_h__
#define __frame_h__

typedef struct{
    unsigned int length;
    unsigned char *data;
}frame_t;

frame_t* initFrame();
void closeFrame();
unsigned char loadNextFrame();

#endif
