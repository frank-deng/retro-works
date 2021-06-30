#include <stdio.h>
#include <malloc.h>
#include <errno.h>
#include "frame.h"

typedef struct{
    unsigned short datalen;
    unsigned long offset;
} frame_meta_t;
static frame_meta_t *frameMetaData=NULL, *currentFramePtr;
static unsigned int frameCount=0, currentFrame=0;
static FILE* fp=NULL;
static frame_t frameBuffer={0,NULL};

frame_t* initFrame(){
    unsigned int largestFrameDataSize=0,datalen,i;
    //Open data file
    fp=fopen("badapple.dat","rb");
    if(NULL==fp){
        perror("Failed to load video data");
        return NULL;
    }

    //Get how many frames
    fseek(fp,4,SEEK_SET);
    fread(&frameCount,sizeof(unsigned int),1,fp);

    //Load meta data
    currentFramePtr=frameMetaData=(frame_meta_t*)malloc(sizeof(frame_meta_t)*frameCount);
    if(NULL==frameMetaData){
        perror("Out of memory");
        return NULL;
    }
    fseek(fp,6,SEEK_SET);
    fread(frameMetaData,sizeof(frame_meta_t),frameCount,fp);

    //Get the lagest frame data, then allocate the appropriate size
    for(i=0;i<frameCount;i++){
        datalen=frameMetaData[i].datalen;
        if(datalen>largestFrameDataSize){
            largestFrameDataSize=datalen;
        }
    }
    frameBuffer.data=(unsigned char *)malloc(sizeof(unsigned char)*largestFrameDataSize);
    if(NULL==frameBuffer.data){
        perror("Out of memory");
        return NULL;
    }

    //Load the first frame
    fseek(fp,6+sizeof(frame_meta_t)*frameCount,SEEK_SET);
    loadNextFrame();

    return &frameBuffer;
}
void closeFrame(){
    if(NULL!=fp){
        fclose(fp);
        fp=NULL;
    }
    if(NULL!=frameBuffer.data){
        free(frameBuffer.data);
        frameBuffer.length=0;
        frameBuffer.data=NULL;
    }
    if(NULL!=frameMetaData){
        free(frameMetaData);
        frameMetaData=NULL;
    }
    frameCount=0;
    currentFrame=0;
}
unsigned char loadNextFrame(){
    unsigned short length=currentFramePtr->datalen;
    if(currentFrame>=frameCount){
        return 0;
    }
    frameBuffer.length=length;
    fread(frameBuffer.data,sizeof(unsigned char),length,fp);
    currentFrame++;
    currentFramePtr++;
    return 1;
}

