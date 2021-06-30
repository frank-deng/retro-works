#ifndef __wav_h__
#define __wav_h__

#include <stdio.h>
#include <io.h>

typedef unsigned char uint8_t;
//typedef unsigned int uint16_t;
typedef unsigned long uint32_t;

#define WAV_BUFFER_SIZE 512
#define WAV_DATA_OFFSET 44
typedef struct{
    unsigned short format;
    unsigned short channels;
    unsigned long sampleRate;
    unsigned long byteRate;
    unsigned short blockAlign;
    unsigned short bitsPerSample;
}audio_format_t;
typedef struct{
    uint16_t length;
    uint16_t offset;
    uint8_t data [WAV_BUFFER_SIZE];
}audio_buffer_t;
typedef struct{
    FILE *fp;
    uint16_t frequency;
    audio_buffer_t audioBuffer[2];
    audio_buffer_t* audioBufferUse;
    audio_buffer_t* audioBufferLoad;
}wav_t;

wav_t* openWAV(char *path);
void closeWAV(wav_t* wav);
uint8_t getSample(wav_t *wav);
void switchWAVBuffer(wav_t *wav);
uint8_t readWAVBuffer(wav_t *wav);

#endif
