;How to compile
;wasm -fo=drawchar.obj drawchar.asm
;wlink NAME drawchar.bin FILE drawchar.obj SYSTEM DOS COM
;Parameter format: Width(Word),Height(Word),XPos(Word),YPos(Word),Color(Byte)

.model tiny
.8086
assume cs:code,ds:code,es:code,ss:code
code segment
org 100h

start:
push si
mov si,0 ;Addr of param
push di
mov di,0 ;Addr of bitmap
push ax
mov ax,0 ;Segment of param
push bx
mov bx,0 ;Segment of bitmap
push cx
push dx
push ds
push es
push bp
push word ptr[si+2]
mov ds,ax
mov es,bx
mov ah,0x0c
mov al,byte ptr[si+8]
mov dx,word ptr[SI+6]
YLoop:
mov cx,word ptr[SI+4]
mov bp,word ptr[SI]
mov bh,0x80
XLoop:
mov bl,bh
and bl,byte ptr[es:di]
jz DrawingEnd
int 0x10
DrawingEnd:
dec bp
jz XLoopEnd
inc cx
cmp bh,1
jne NextByteEnd
inc di
NextByteEnd:
ror bh,1
jmp XLoop
XLoopEnd:
inc di
inc dx
sub word ptr[si+2],1
jnz YLoop
FinallyExit:
pop word ptr[si+2]
pop bp
pop es
pop ds
pop dx
pop cx
pop bx
pop ax
pop di
pop si
retf

code ends
end start

