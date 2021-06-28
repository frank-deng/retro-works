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
static __inline void drawBlock(unsigned int baseOffset, unsigned char *data){
    //unsigned int baseOffset=(y*40*4)+x;
    unsigned char *pdata=data;
    unsigned int __far *vmem_ptr = vmem+baseOffset;
    //Odd lines
    *vmem_ptr=valueConvertTable[*pdata];
    vmem_ptr+=40;
    pdata++;
    *vmem_ptr=valueConvertTable[*pdata];
    vmem_ptr+=40;
    pdata++;
    *vmem_ptr=valueConvertTable[*pdata];
    vmem_ptr+=40;
    pdata++;
    *vmem_ptr=valueConvertTable[*pdata];
    pdata++;
    //Even lines
    vmem_ptr = vmem+4096+baseOffset;
    *vmem_ptr=valueConvertTable[*pdata];
    vmem_ptr+=40;
    pdata++;
    *vmem_ptr=valueConvertTable[*pdata];
    vmem_ptr+=40;
    pdata++;
    *vmem_ptr=valueConvertTable[*pdata];
    vmem_ptr+=40;
    pdata++;
    *vmem_ptr=valueConvertTable[*pdata];
}
static __inline void drawBlackBlock(unsigned int baseOffset){
    unsigned int __far *vmem_ptr = vmem+baseOffset;
    //Odd lines
    *vmem_ptr=0;
    vmem_ptr+=40;
    *vmem_ptr=0;
    vmem_ptr+=40;
    *vmem_ptr=0;
    vmem_ptr+=40;
    *vmem_ptr=0;
    //Even lines
    vmem_ptr = vmem+4096+baseOffset;
    *vmem_ptr=0;
    vmem_ptr+=40;
    *vmem_ptr=0;
    vmem_ptr+=40;
    *vmem_ptr=0;
    vmem_ptr+=40;
    *vmem_ptr=0;
}
static __inline void drawWhiteBlock(unsigned int baseOffset){
    unsigned int __far *vmem_ptr = vmem+baseOffset;
    //Odd lines
    *vmem_ptr=0xffff;
    vmem_ptr+=40;
    *vmem_ptr=0xffff;
    vmem_ptr+=40;
    *vmem_ptr=0xffff;
    vmem_ptr+=40;
    *vmem_ptr=0xffff;
    //Even lines
    vmem_ptr = vmem+4096+baseOffset;
    *vmem_ptr=0xffff;
    vmem_ptr+=40;
    *vmem_ptr=0xffff;
    vmem_ptr+=40;
    *vmem_ptr=0xffff;
    vmem_ptr+=40;
    *vmem_ptr=0xffff;
}
void drawFrame(unsigned char *data,unsigned int len){
    unsigned int mark,offset;
    unsigned char *p=data, bx, by;
    while(p<data+len){
        mark=*((unsigned int *)p);
        p+=2;
        offset=mark&0x3fff;
        //Convert offset of original video to the one used by CGA
        if(mark & 0x4000){
            drawBlackBlock(offset);
        }else if(mark & 0x8000){
            drawWhiteBlock(offset);
        }else{
            drawBlock(offset,p);
            p+=8;
        }
    }
}
