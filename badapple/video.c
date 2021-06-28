#include "video.h"

void setVideoMode(unsigned char mode);
#pragma aux setVideoMode = \
    "mov ah,0"\
    "int 10h"\
    modify [ax]\
    parm [al];

void initVideo(){
    setVideoMode(4);
}
void closeVideo(){
    setVideoMode(3);
}
