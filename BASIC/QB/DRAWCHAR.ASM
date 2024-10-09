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
push ds
push es
push si
push di
push ax
mov si,0 ;Addr of param
mov ax,0 ;Segment of param
mov ds,ax
mov di,0 ;Addr of bitmap
mov ax,0 ;Segment of bitmap
mov es,ax
push bx
push cx
push dx

mov ax,word ptr[si+2]
mov word ptr[cs:YCounter],ax
mov dx,word ptr[SI+6]
mov al,byte ptr[si+8]

YLoop:
mov cx,word ptr[SI+4]
mov bx,word ptr[SI]
mov ah,0x80

XLoop:
push ax
and ah,byte ptr[es:di]
jz DrawingEnd
mov ah,0x0c
int 0x10

DrawingEnd:
pop ax
dec bx
jz XLoopEnd

inc cx
cmp ah,1
jne NextByteEnd
inc di
NextByteEnd:
ror ah,1
jmp XLoop

XLoopEnd:
inc di
inc dx
sub word ptr[si+2],1
jnz YLoop

FinallyExit:
pop dx
pop cx
pop bx
pop ax
pop di
pop si
pop es
pop ds
retf

YCounter:
dw 0
code ends
end start
