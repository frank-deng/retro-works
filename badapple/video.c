#include "video.h"
#include "frame.h"

static unsigned int __far *vmem=0xb8000000L;
static unsigned int valueConvertTable[256];
void setVideoMode(unsigned char mode);
#pragma aux setVideoMode = \
    "mov ah,0"\
    "int 10h"\
    modify [ax]\
    parm [al];

static unsigned int expandValue(unsigned char src){
    int i;
    unsigned int result=0;
    for(i=7; i>=0; i--){
        if(src&(1<<i)){
            result|=3;
        }
        if(i){
            result<<=2;
        }
    }
    result=(result<<8) | ((result>>8)&0xff);
    return result;
}
void initVideo(){
    unsigned int i;
    for(i=0;i<256;i++){
        valueConvertTable[i]=expandValue(i);
    }
    setVideoMode(4);
}
void closeVideo(){
    setVideoMode(3);
}
static void drawBlock(unsigned char x, unsigned char y, unsigned char *data){
    unsigned char i;
    unsigned int baseOffset=(y*40*4)+x;
    unsigned int __far *vmem_ptr = vmem+baseOffset;
    //Odd lines
    for(i=0;i<7;i+=2){
        *vmem_ptr=valueConvertTable[data[i]];
        vmem_ptr+=40;
    }
    //Even lines
    vmem_ptr = vmem+4096+baseOffset;
    for(i=1;i<8;i+=2){
        *vmem_ptr=valueConvertTable[data[i]];
        vmem_ptr+=40;
    }
}
void drawBlankBlock(unsigned char x, unsigned char y, unsigned char color){
    unsigned char i;
    unsigned int baseOffset=baseOffset=(y*40*4)+x, colorValue=color?0xffff:0;
    unsigned int __far *vmem_ptr = vmem+baseOffset;
    //Odd lines
    for(i=0;i<7;i+=2){
        *vmem_ptr=colorValue;
        vmem_ptr+=40;
    }
    //Even lines
    vmem_ptr = vmem+4096+baseOffset;
    for(i=1;i<8;i+=2){
        *vmem_ptr=colorValue;
        vmem_ptr+=40;
    }
}
void drawFrame(unsigned char *data,unsigned int len){
    unsigned int mark,offset;
    unsigned char *p=data, bx, by;
    while(p<data+len){
        mark=*((unsigned int *)p);
        p+=2;
        offset=mark&0x3fff;
        //Convert offset of original video to the one used by CGA
        bx=(offset % (FRAME_WIDTH/8))+10;
        by=(offset / (FRAME_WIDTH/8))+6;
        if(mark & 0x4000){
            drawBlankBlock(bx,by,0);
        }else if(mark & 0x8000){
            drawBlankBlock(bx,by,1);
        }else{
            drawBlock(bx,by,p);
            p+=8;
        }
    }
}
