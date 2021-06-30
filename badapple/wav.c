#include <stdio.h>
#include <malloc.h>
#include <errno.h>
#include "wav.h"

wav_t* openWAV(char *path){
    audio_format_t audioFormat;
    wav_t* wav;

    //Prepare wav struct
    wav=(wav_t*)malloc(sizeof(wav_t));
    if(NULL==wav){
        perror("Out of memory");
        return NULL;
    }
    wav->audioBufferUse=wav->audioBuffer;
    wav->audioBufferLoad=wav->audioBuffer+1;
    wav->audioBufferUse->length=wav->audioBufferUse->offset=0;
    wav->audioBufferLoad->length=wav->audioBufferLoad->offset=0;

    //Open file
    wav->fp=fopen(path,"rb");
    if(NULL==wav->fp){
        perror("Failed to open WAV file");
        free(wav);
        return NULL;
    }

    //Read audio format info
    fseek(wav->fp,20,SEEK_SET);
    fread(&audioFormat, sizeof(audio_format_t),1,wav->fp);
    wav->frequency=audioFormat.sampleRate;

    //Initialize audio buffer
    fseek(wav->fp,WAV_DATA_OFFSET,SEEK_SET);
    readWAVBuffer(wav);
    switchWAVBuffer(wav);

    return wav;
}
void closeWAV(wav_t* wav){
    if(NULL!=wav->fp){
        fclose(wav->fp);
    }
    free(wav);
}
uint8_t getSample(wav_t *wav){
    audio_buffer_t *audio_buffer=wav->audioBufferUse;
    uint8_t value;
    if(audio_buffer->offset >= audio_buffer->length){
        return audio_buffer->data[audio_buffer->length-1];
    }
    value=audio_buffer->data[audio_buffer->offset];
    audio_buffer->offset++;
    return value;
}
void switchWAVBuffer(wav_t *wav){
    audio_buffer_t *temp=wav->audioBufferUse;
    wav->audioBufferUse=wav->audioBufferLoad;
    wav->audioBufferLoad=temp;
}
uint8_t readWAVBuffer(wav_t *wav){
    audio_buffer_t *audio_buffer=wav->audioBufferLoad;
    audio_buffer->length=fread(audio_buffer->data, sizeof(uint8_t), WAV_BUFFER_SIZE, wav->fp);
    audio_buffer->offset=0;
    return 1;
}
