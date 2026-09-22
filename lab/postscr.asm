;How to compile
;wasm -fo=postscr.obj postscr.asm
;wlink NAME postscr.com FILE postscr.obj SYSTEM DOS COM
.model tiny
.8086
assume cs:code,ds:code,es:code,ss:code
code segment
org 100h
start:
cld
push es
mov ax,0b800h
mov es,ax
xor di,di
mov ax,0700h
mov cx,2000
rep stosw
pop es
mov cx,41
xor si,si
mov bp,offset memstr
print_mem:
mov bl,100
mov di,bp
mov ax,si
div bl
mov bl,ah
aam
or ax,03030h
xchg ah,al
stosw
mov al,bl
aam
or ax,03030h
xchg ah,al
stosw
push cx
mov ax,01301h
mov bx,7
mov cx,8
xor dx,dx
int 10h
pop cx
mov bx,1
call sleep
add si,16
loop print_mem
mov bx,8
call sleep
in al,061h
or al,03h
out 61h,al
mov al,0b6h
out 43h,al
mov al,0f0h
out 42h,al
mov al,05h
out 42h,al
mov bx,2
call sleep
in al,61h
and al,0FCh
out 061h,al
mov ah,2
mov dx,0200h
int 10h
mov ax,4C00h
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
memstr db "0000K OK"
code ends
end start

