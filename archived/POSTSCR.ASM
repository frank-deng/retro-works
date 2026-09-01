;How to compile
;wasm -fo=postscr.obj postscr.asm
;wlink NAME postscr.com FILE postscr.obj SYSTEM DOS COM
.model tiny
.8086
assume cs:code,ds:code,es:code,ss:code
code segment
org 100h
start:
push es
mov ax,0b800h
mov es,ax
xor di,di
mov ax,0700h
mov cx,2000
cld
rep stosw
pop es
xor si,si
print_mem:
mov ah,2
xor dx,dx
xor bh,bh
int 10h
mov al,'0'
mov ah,0eh
int 10h
mov bx,100
mov ax,si
div bx
add al,'0'
mov ah,0eh
int 10h
mov ax,dx
aam
mov bx,ax
add bh,'0'
add bl,'0'
mov ah,0eh
mov al,bh
int 10h
mov ah,0eh
mov al,bl
int 10h
mov ax,01301h
mov bx,7
mov cx,offset memstrend-offset memstr
mov dx,4
mov bp,offset memstr
int 10h
mov bx,1
call sleep
cmp si,640
jge mem_finish
add si,16
jmp print_mem
mem_finish:
mov bx,8
call sleep
in al,061h
or al,03h
out 0x61,al
mov al,0xb6
out 0x43,al
mov al,0xf0
out 0x42,al
mov al,0x05
out 0x42,al
mov bx,2
call sleep
in al,0x61
and al,0FCh
out 061h,al
mov ah,2
mov dx,0100h
xor bh,bh
int 10h
mov bx,20
call sleep
mov ah,2
mov dx,0200h
xor bh,bh
int 10h
mov ax, 4C00h
int 21h
sleep:
push ax
push cx
push dx
push si
xor ax,ax
int 1ah
mov si,dx
waitloop:
hlt
int 1ah
cmp dx,si
je waitloop
mov si,dx
dec bx
jnz waitloop
pop si
pop dx
pop cx
pop ax
ret
memstr db "K OK"
memstrend:
code ends
end start

