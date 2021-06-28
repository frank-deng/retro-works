#include <stdio.h>
#include <malloc.h>
#include "frame.h"

typedef struct frame_meta_t_def{
    unsigned int length;
    unsigned long offset;
} frame_meta_t;
static frame_meta_t *frameMetaData=NULL;
static FILE* fp=NULL;
static unsigned int frameCount=0;

unsigned char initFrame(){
    //Open data file
    FILE *fp=fopen("badapple.dat","rb");
    if(NULL==fp){
        puts("Failed to load video data");
        return 0;
    }

    //Get how many frames
    fseek(fp,4,SEEK_SET);
    fread(&frameCount,sizeof(unsigned int),1,fp);

    //Load meta data
    frameMetaData=malloc(sizeof(frame_meta_t)*frameCount);
    if(NULL==frameMetaData){
        puts("Out of memory");
        return 0;
    }
    fseek(fp,6,SEEK_SET);
    fread(frameMetaData,sizeof(frame_meta_t),frameCount,fp);

    //Init meta data
    return 1;
}
void closeFrame(){
    fclose(fp);
    free(frameMetaData);
    frameMetaData=NULL;
    frameCount=0;
}
unsigned int getFrameCount(){
    return frameCount;
}
unsigned int getFrameData(unsigned char *buffer, unsigned int frameIdx){
    unsigned int length=(frameMetaData[frameIdx].length);
    fseek(fp,frameMetaData[frameIdx].offset,SEEK_SET);
    fread(buffer,sizeof(unsigned char),length,fp);
    printf("%u %x %u\n",frameIdx,frameMetaData[frameIdx].offset,frameMetaData[frameIdx].length);
    return length;
}

