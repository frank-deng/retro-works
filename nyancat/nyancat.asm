org 100h

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
mov [Port61hValueOrig],al
or al,0x3
out 0x61,al

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
mov al,0xb6
out 0x43,al
mov si,word[CurrentMusicNote]
shl si,1
add si,FrequencyList
mov ax,word[si]
out 0x42,al
mov ah,al
out 0x42,al

;Sleep 100ms
push cx
mov ax,0x8600
mov cx,1
mov dx,8600
int 15h
pop cx

;Next Note
mov ax,[MusicLength]
cmp word[CurrentMusicNote],ax
jne UseNextNote
mov word[CurrentMusicNote],0
jmp NextNoteEnd
UseNextNote:
inc word[CurrentMusicNote]
NextNoteEnd:

;Next frame
cmp byte[FrameIdx],11
jnae UseNextFrame
mov byte[FrameIdx],0
jmp mainLoop
UseNextFrame:
inc byte[FrameIdx]
jmp mainLoop

exitProgram:

;Revert speaker status
mov al,[Port61hValueOrig]
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

;Enable 16 color for background
mov ax,0x1003
mov bl,1
int 10h

;Exit to dos
mov ah,4ch
int 21h

FrameIdx:
db 0

CurrentMusicNote:
dw 0

Port61hValueOrig:
db 0

FrameData:
%include "frames.inc"

%include "music.inc"

