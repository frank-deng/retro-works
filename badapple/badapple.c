#include <stdio.h>
#include <conio.h>
#include <dos.h>

typedef struct frame_meta_t_def{
    unsigned int length;
    unsigned long offset;
    void far* frameData;
} frame_meta_t;
static unsigned int frameCount=0;
static frame_meta_t *frameMetaData=NULL;

int main(){
    FILE *fp=fopen("badapple.dat","rb");
    if(NULL==fp){
        puts("Failed to load video data");
        return 1;
    }

    //Get how many frames
    fseek(fp,4);
    fread(&frameCount,sizeof(unsigned int),1,fp);

    //Load meta data
    frameMetaData=malloc(sizeof(frame_meta_t)*frameCount);
    if(NULL==frameMetaData){
        puts("Out of memory");
        return 1;
    }
    fseek(fp,6);
    fread(frameMetaData,sizeof(frame_meta_t),frameCount,fp);

    //Setup timer for every 125/4 ms, orig timer vector called every time
	outb(0x43,0x52);
    outp(0x40,0xa7);
    outp(0x40,0x91);
    timerOrig=_dos_getvect(0x8);

    //Free resources
    _dos_setvect(0x8,timerOrig);
	outb(0x43,0x52);
    outp(0x40,0xff);
    outp(0x40,0xff);
    free(frameMetaData);

    return 0;
}
