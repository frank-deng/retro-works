.8086
.model tiny
.code
org 100h
start:


doexit:
mov sp,bp
pop bp
mov ax, 4C00h
int 21h

newline db '&',0dh,0ah,'$'

end start

num2str:
push cx
push dx
