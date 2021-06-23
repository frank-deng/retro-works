#include "frames.h"

//Keyboard and sleep
inline unsigned char getkey();
#pragma aux getkey=\
    "mov ax,0x0100"\
    "int 0x16"\
    "jz noinput"\
    "mov ax,0"\
    "int 0x16"\
    "jmp end"\
"noinput:"\
    "mov ax,0"\
"end:"\
    modify [ax]\
    value [ah];

inline void sleep(unsigned int h, unsigned int l);
#pragma aux sleep=\
    "mov ax, 0x8600"\
    "int 0x15"\
    modify [ax cx dx]\
    parm [cx] [dx];

//Video related
static unsigned char __far *video_pointer=(unsigned char far *)0xb8000000L;
inline void setScreenMode();
#pragma aux setScreenMode=\
    "mov ax, 0x1003"\
	"mov bl, 0"\
    "int 0x10"\
    modify [ax bx];
inline void revertScreenMode();
#pragma aux revertScreenMode=\
    "mov ax, 0x1003"\
	"mov bl, 1"\
    "int 0x10"\
    modify [ax bx];
inline void initScreen(){
    unsigned int i;
    setScreenMode();
    for(i=0; i<4000; i+=2){
        video_pointer[i]=0xdc;
        video_pointer[i+1]=0x00;
    }
}
inline void drawFrame(unsigned char *frame){
    unsigned int i;
    for(i=0; i<2000; i++){
        video_pointer[(i<<1)|1]=frame[i];
    }
}
inline void clearScreen(){
    unsigned int i;
    revertScreenMode();
    for(i=0; i<4000; i+=2){
        video_pointer[i]=0;
        video_pointer[i+1]=7;
    }
}

void main(){
    unsigned char frame=0;

    //Initialization
    initScreen();

    //Main works
    while(1){
        if(0x1==getkey()){
            break;
        }
        drawFrame(FRAMES_DATA[frame]);
        if(frame>=11){
            frame=0;
        }else{
            frame++;
        }
        //sleep(0x1,0x86a0);
    }

    //Clean up works
    clearScreen();
}
