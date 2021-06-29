#include <stdio.h>
#include <dos.h>
#include <conio.h>
#include <malloc.h>
#include <errno.h>

typedef unsigned char uint8_t;
typedef unsigned int uint16_t;
typedef unsigned long uint32_t;

void hlt();
#pragma aux hlt = "hlt";
void cli();
#pragma aux cli = "cli";
void sti();
#pragma aux sti = "sti";

/*
Keyboard related code
*/
void clearKeyboardBuffer();
#pragma aux clearKeyboardBuffer = \
    "CheckKeyInput:"\
    "mov ax,0x0100"\
    "int 16h"\
    "je CheckKeyboardEnd"\
    "mov ax,0"\
    "int 16h"\
    "jmp CheckKeyInput"\
    "CheckKeyboardEnd:"\
    modify [ax];

static void (__interrupt __far * keyboardHandlerOrig)();
static unsigned char keypressed=0;
static void __interrupt keyboardHandler(){
    while(inp(0x64)&0x1){
        keypressed=inp(0x60);
    }
    outp(0xa0,0x20);
    outp(0x20,0x20);
}
void initKeyboard(){
    keyboardHandlerOrig=_dos_getvect(0x09);
    _dos_setvect(0x09,keyboardHandler);
}
void closeKeyboard(){
    _dos_setvect(0x09,keyboardHandlerOrig);
    clearKeyboardBuffer();
}
unsigned char getKeypressed(){
    unsigned char value=keypressed;
    keypressed=0;
    return value;
}

/*
WAV loader
*/
#define WAV_BUFFER_SIZE 1024
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
    uint8_t status; //bit0: Which buffer to use, bit1:Whether buffer has been updated by timer
    uint16_t frequency;
    audio_buffer_t audioBuffer[2];
}wav_t;
uint8_t readWAVBuffer(wav_t *wav);
wav_t* openWAV(char *path){
    audio_format_t audioFormat;
    wav_t* wav;

    //Prepare wav struct
    wav=(wav_t*)malloc(sizeof(wav_t));
    if(NULL==wav){
        perror("Out of memory");
        return NULL;
    }
    wav->status=0;

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
    int audioBufferUse=(wav->status & 1 ? 1 : 0);
    audio_buffer_t *audio_buffer=wav->audioBuffer+audioBufferUse;
    uint8_t value=audio_buffer->data[audio_buffer->offset];
    if(audio_buffer->length){
        audio_buffer->offset++;
        if(audio_buffer->offset >= audio_buffer->length){
            if(audioBufferUse){
                wav->status&=0xfe;
            }else{
                wav->status|=0x1;
            }
        }
    }
    wav->status |= 0x2;
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
    int i;
    for(i=0;i<2;i++,audio_buffer++){
        if(audio_buffer->length<=audio_buffer->offset){
            audio_buffer->length=fread(audio_buffer->data, sizeof(uint8_t), WAV_BUFFER_SIZE, wav->fp);
            audio_buffer->offset=0;
            if(fseek(wav->fp,WAV_BUFFER_SIZE,SEEK_CUR)){
                return 0;  //Should not be called again since file end reached
            }
        }
    }
    return 1;
}


/*
Timer related code
*/
static wav_t *wavInstance;
static uint8_t Port61hValueOrig;
static void (__interrupt __far * timerHandlerOrig)();
void __interrupt timerHandler(){
    uint16_t value=getSample(wavInstance);
    uint16_t microsec=(value*60/255);
    outp(0x43,0x96);
    outp(0x42,microsec&0xff);
    outp(0x20,0x20);
}
void initTimer(unsigned int reloadValue){
    timerHandlerOrig=_dos_getvect(0x08);
    _dos_setvect(0x08,timerHandler);
    puts("ok");
    if(reloadValue<0xff){
        outp(0x43,0x14);
        outp(0x40,reloadValue&0xff);
    }else{
        puts("ok1");
        outp(0x43,0x34);
        printf("%u\n",reloadValue);
        outp(0x40,reloadValue&0xff);
        outp(0x40,(reloadValue>>8)&0xff);
        puts("ok2");
    }
    Port61hValueOrig=inp(0x61);
    outp(0x61,Port61hValueOrig&0x3);
    puts("ok3");
}
void closeTimer(){
    outp(0x61,Port61hValueOrig);
    _dos_setvect(0x08,timerHandlerOrig);
	outp(0x43,0x52);
    outp(0x40,0xff);
    outp(0x40,0xff);
}

/*
Main code
*/
int main(int argc, char* argv[]){
    if(argc<2){
        printf("Usage: %s file.wav\n",argv[0]);
        return 1;
    }

    wavInstance=openWAV(argv[1]);
    if(NULL==wavInstance){
        return 1;
    }
    puts("WAV loaded");
    //initKeyboard();
    //initTimer(3579545L / wavInstance->frequency);
    initTimer(874);

    puts("Start playing");
    while(1){
        waitBufferUpdate(wavInstance);
        readWAVBuffer(wavInstance);
    }

    puts("Exit");
    //closeKeyboard();
    closeTimer();
    closeWAV(wavInstance);
    return 0;
}
