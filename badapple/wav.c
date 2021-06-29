#include <stdio.h>
#include <malloc.h>
#include <errno.h>
#include "wav.h"

static __inline void hlt();
#pragma aux hlt = "hlt";
static __inline void cli();
#pragma aux cli = "cli";
static __inline void sti();
#pragma aux sti = "sti";

wav_t* openWAV(char *path){
    audio_format_t audioFormat;
    wav_t* wav;

    //Prepare wav struct
    wav=(wav_t*)malloc(sizeof(wav_t));
    if(NULL==wav){
        perror("Out of memory");
        return NULL;
    }

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
    wav->audioBuffer[0].length=wav->audioBuffer[0].offset=0;
    wav->audioBuffer[1].length=wav->audioBuffer[1].offset=0;
    wav->status=1;
    readWAVBuffer(wav);
    wav->status=0;
    readWAVBuffer(wav);

    return wav;
}
void closeWAV(wav_t* wav){
    if(NULL!=wav->fp){
        fclose(wav->fp);
    }
    free(wav);
}
uint8_t getSample(wav_t *wav){
    unsigned char audioBufferUse=(wav->status & 1 ? 1 : 0);
    audio_buffer_t *audio_buffer=wav->audioBuffer+audioBufferUse;
    uint8_t value;
    if(!audio_buffer->length){
        return 0;
    }
    value=audio_buffer->data[audio_buffer->offset];
    audio_buffer->offset++;
    //Switch to another buffer, then discard current buffer
    if(audio_buffer->offset >= audio_buffer->length){
        audio_buffer->offset=audio_buffer->length=0;
        if(audioBufferUse){
            wav->status&=0xfe;
        }else{
            wav->status|=0x1;
        }
        wav->status |= 0x2;
    }
    return value;
}
void waitBufferUpdate(wav_t *wav){
    while(!(wav->status & 0x2)){
        hlt();
    }
    wav->status &= (~0x2);
}
uint8_t readWAVBuffer(wav_t *wav){
    audio_buffer_t *audio_buffer=wav->audioBuffer;
    cli();
    if(!(wav->status&1)){
        audio_buffer++;
    }
    if(0!=audio_buffer->length){
        sti();
        return 0;
    }
    audio_buffer->length=fread(audio_buffer->data, sizeof(uint8_t), WAV_BUFFER_SIZE, wav->fp);
    audio_buffer->offset=0;
    sti();
    return 1;
}
