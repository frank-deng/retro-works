include common.inc
.model tiny
.8086
extrn s16toa:near
.code
org 100h
start:
push bp
mov bp,sp
sub sp,666
memset ss,[bp-666],0,333

mov ax,ss
mov es,ax
mov ds,ax
mov ax,23456
lea di,[bp-666]
call s16toa
mov ah,40h
mov bx,1
lea dx,[bp-666]
int 21h

doexit:
mov sp,bp
pop bp
mov ax, 4C00h
int 21h
end start
