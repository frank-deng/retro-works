.8086
.model tiny
include common.inc
extrn itoa:cPType
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
call itoa
mov ah,40h
mov bx,1
lea dx,[bp-666]
int 21h
mov ax,-1
lea di,[bp-666]
call itoa
mov ah,40h
mov bx,1
lea dx,[bp-666]
int 21h
mov ax,-32768
lea di,[bp-666]
call itoa
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
