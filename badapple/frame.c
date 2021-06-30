#include <malloc.h>
#include <errno.h>
#include "frame.h"

frame_t* initFrame(){
    frame_t *frame;
    uint16_t largestFrameDataSize=0,datalen,i;
    //Prepare data structure
    frame=(frame_t*)malloc(sizeof(frame_t));
    if(NULL==frame){
        perror("Out of memory");
        return NULL;
    }
    frame->currentFrame=0;
    frame->frameCount=0;
    frame->bufferLength=0;

    //Open data file
    frame->fp=fopen("badapple.dat","rb");
    if(NULL==frame->fp){
        perror("Failed to load video data");
        free(frame);
        return NULL;
    }

    //Get how many frames
    fseek(frame->fp,4,SEEK_SET);
    fread(&(frame->frameCount),sizeof(uint16_t),1,frame->fp);

    //Load meta data
    frame->frameLenArr=(uint16_t*)malloc(sizeof(uint16_t)*frame->frameCount);
    if(NULL==frame->frameLenArr){
        perror("Out of memory");
        fclose(frame->fp);
        free(frame);
        return NULL;
    }
    fseek(frame->fp,6,SEEK_SET);
    fread(frame->frameLenArr,sizeof(uint16_t),frame->frameCount,frame->fp);

    //Get the lagest frame data, then allocate the appropriate size
    for(i=0;i<frame->frameCount;i++){
        datalen=frame->frameLenArr[i];
        if(datalen>largestFrameDataSize){
            largestFrameDataSize=datalen;
        }
    }
    frame->buffer=(uint8_t*)malloc(sizeof(uint8_t)*largestFrameDataSize);
    if(NULL==frame->buffer){
        perror("Out of memory");
        free(frame->frameLenArr);
        fclose(frame->fp);
        free(frame);
        return NULL;
    }

    //Load the first frame
    fseek(frame->fp,6+sizeof(uint16_t)*frame->frameCount,SEEK_SET);
    loadNextFrame(frame);

    return frame;
}
void closeFrame(frame_t *frame){
    if(NULL!=frame->fp){
        fclose(frame->fp);
        frame->fp=NULL;
    }
    if(NULL!=frame->buffer){
        free(frame->buffer);
        frame->buffer=NULL;
        frame->bufferLength=0;
    }
    if(NULL!=frame->frameLenArr){
        free(frame->frameLenArr);
        frame->frameLenArr=NULL;
    }
    frame->currentFrame=frame->frameCount=0;
    free(frame);
}
unsigned char loadNextFrame(frame_t *frame){
    unsigned short length=0;
    if(frame->currentFrame>=frame->frameCount){
        return 0;
    }
    length=frame->frameLenArr[frame->currentFrame];
    frame->bufferLength=length;
    if(length){
        fread(frame->buffer,sizeof(uint8_t),length,frame->fp);
    }
    frame->currentFrame++;
    return 1;
}

