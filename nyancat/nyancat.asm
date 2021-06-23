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

;Sleep 100ms
push cx
mov ax,0x8600
mov cx,1
mov dx,8600
int 15h
pop cx

;Next frame
cmp byte[FrameIdx],11
jnae UseNextFrame
mov byte[FrameIdx],0
jmp mainLoop
UseNextFrame:
inc byte[FrameIdx]
jmp mainLoop

exitProgram:

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

FrameData:
%include "frames.inc"

