#include <stdio.h>
#include <malloc.h>
#include <errno.h>
#include "frame.h"

typedef struct frame_meta_t_def{
    unsigned short datalen;
    unsigned long offset;
} frame_meta_t;
static frame_meta_t *frameMetaData=NULL;
static FILE* fp=NULL;
static unsigned int frameCount=0;

unsigned char initFrame(){
    //Open data file
    fp=fopen("badapple.dat","rb");
    if(NULL==fp){
        perror("Failed to load video data");
        return 0;
    }

    //Get how many frames
    fseek(fp,4,SEEK_SET);
    fread(&frameCount,sizeof(unsigned int),1,fp);

    //Load meta data
    frameMetaData=(frame_meta_t*)malloc(sizeof(frame_meta_t)*frameCount);
    if(NULL==frameMetaData){
        perror("Out of memory");
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
    unsigned short length=frameMetaData[frameIdx].datalen;
    fseek(fp,frameMetaData[frameIdx].offset,SEEK_SET);
    fread(buffer,sizeof(unsigned char),length,fp);
    return length;
}

