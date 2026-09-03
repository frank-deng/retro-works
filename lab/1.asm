.8086
.model tiny
include common.inc
extrn uitoa:cPType
extrn itoa:cPType
extrn atoui:cPType
extrn atoi:cPType
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

lea si,sample_num
mov cx,sample_num_end-sample_num
call atoui
lea di,[bp-666]
call itoa
mov ah,40h
mov bx,1
lea dx,[bp-666]
int 21h

lea si,sample_num2
mov cx,sample_num2_end-sample_num2
call atoi
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

sample_num db "666"
sample_num_end:
sample_num2 db "-666"
sample_num2_end:
end start

