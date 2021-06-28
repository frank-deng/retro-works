#include <dos.h>
#include <conio.h>
#include "keyboard.h"

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
    (*keyboardHandlerOrig)();
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
