%define MusicDelay 1
%define FrameDelay 0

org 100h
jmp start

;Data area
FrameIdx:
db 0
CurrentMusicNote:
dw 0
FrameDelayTicks:
db 0
MusicDelayTicks:
db 0
PrevTimerLo:
dw 0
PrevTimerHi:
dw 0
FrameData:
%include "frames.inc"
%include "music.inc"

;Code starts
start:

;Initialize timer
mov ax,0
int 1ah
mov [PrevTimerHi],cx
mov [PrevTimerLo],dx

;Enable 16 color for background
mov ax,0x1003
mov bl,0
int 10h

;Video buffer start address
mov ax,0xb800
mov es,ax

;Initialize screen
mov bx,0
initScreen:
mov word[es:bx], 0x00dc
add bx,2
cmp bx,4000
jnae initScreen

;Initialize speaker
in al,0x61
or al,0x3
out 0x61,al
mov al,0xb6
out 0x43,al

;Start looping frames
mainLoop:

;Test keyboard
mov ax,0x0100 ;Check if keypress happened
int 16h
jz noInput
mov ax,0
int 0x16
cmp ah,0x1 ;Check if esc is pressed
je exitProgram ;If esc is pressed, then exit
noInput:

;Get frame data address
mov ch,0
mov cl,byte[FrameIdx]
imul cx,2000
add cx,FrameData
mov si,cx
mov bx,1

;Draw frame
DrawFrame:
mov ah,byte[si]
mov byte[es:bx],ah
add bx,2
inc si
cmp bx,4000
jnae DrawFrame

;Set speaker frequency
mov si,word[CurrentMusicNote]
add si,MusicData
mov ch,0
mov cl,byte[si]
shl cx,1
mov si,cx
add si,FrequencyList
mov ax,word[si]
out 0x42,al
mov al,ah
out 0x42,al

;Sleep 100ms
push cx
push dx
WaitLoop:
hlt
mov ax,0
int 1ah
cmp cx,[PrevTimerHi]
jne WaitEnd
cmp dx,[PrevTimerLo]
jne WaitEnd
jmp WaitLoop
WaitEnd:
mov [PrevTimerHi],cx
mov [PrevTimerLo],dx
pop dx
pop cx

;Next Note
cmp byte[MusicDelayTicks],0
jne SkipNextNote
mov byte[MusicDelayTicks],MusicDelay

inc word[CurrentMusicNote]
cmp word[CurrentMusicNote],MusicLength
jnae NextNoteEnd
mov word[CurrentMusicNote],0
jmp NextNoteEnd

SkipNextNote:
dec byte[MusicDelayTicks]
NextNoteEnd:

;Next frame
cmp byte[FrameDelayTicks],0
jne SkipNextFrame
mov byte[FrameDelayTicks],FrameDelay

cmp byte[FrameIdx],11
jnae UseNextFrame
mov byte[FrameIdx],0
jmp NextFrameEnd
UseNextFrame:
inc byte[FrameIdx]
jmp NextFrameEnd

SkipNextFrame:
dec byte[FrameDelayTicks]
NextFrameEnd:

jmp mainLoop

exitProgram:

;Revert speaker status
in al,0x61
and al,0xFC
out 0x61,al

;revert sound frequency to 1000hz
mov al,0xb6
out 0x43,al
mov al,0xff
out 0x42,al
mov al,0x03
out 0x42,al

;Clear screen
mov bx,0
clearScreen:
mov word[es:bx],0x0700
add bx,2
cmp bx,4000
jnae clearScreen

;Revert 16 color for background
mov ax,0x1003
mov bl,1
int 10h

;Exit to dos
mov ah,4ch
int 21h

