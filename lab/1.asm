.8086
.model tiny
include common.inc
include cmdline.inc
extrn uitox:cPType
.code
org 100h
start:
cmdinit
loop_cmdline:
call cmdparse
cmp si,di
je loop_cmdline_end
push cx
mov cx,di
sub cx,si
mov ah,40h
mov bx,1
mov dx,si
int 21h
mov ah,09h
lea dx,[newline]
int 21h
pop cx
jmp loop_cmdline
loop_cmdline_end:

push bp
mov bp,sp
sub sp,666
memset ss,[bp-666],0,333

mov ax,01234h
lea di,[bp-666]
call uitox
mov ah,40h
mov bx,1
mov cx,4
lea dx,[bp-666]
int 21h

mov ax,0abcdh
lea di,[bp-666]
call uitox
mov ah,40h
mov bx,1
mov cx,4
lea dx,[bp-666]
int 21h

mov ah,09h
lea dx,[newline]
int 21h

doexit:
mov sp,bp
pop bp
mov ax, 4C00h
int 21h

newline db '&',0dh,0ah,'$'

end start

