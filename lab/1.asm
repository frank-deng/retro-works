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
memset ss,[bp-666],0,666

mov ax,23456
lea di,[bp-666]
call s16toa
mov ah,40h
mov bx,1
mov dx,di
int 21h

mov sp,bp
pop bp
mov ax, 4C00h
int 21h
end start
