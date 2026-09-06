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
call test_normal
mov ax, 4C00h
int 21h

test_normal:
push bp
mov bp,sp
sub sp,10
push ax
push bx
push cx
push dx
push si
push di
push ds
push es
mov ax,ss
mov ds,ax
mov es,ax
mov bx,1
lea di,[bp-10]
mov si,di
mov word ptr[bp-2],0
test_nums_cycle:
mov ax,word ptr[bp-2]
call itoa
call atoi
cmp ax,word ptr[bp-2]
je test_s16_ok
call test_normal_error
test_s16_ok:
mov ax,word ptr[bp-2]
call uitoa
call atoui
cmp ax,word ptr[bp-2]
je test_u16_ok
call test_normal_error
je test_u16_ok
test_u16_ok:
inc word ptr[bp-2]
jnz test_nums_cycle
pop es
pop ds
pop di
pop si
pop dx
pop cx
pop bx
pop ax
mov sp,bp
pop bp
ret

test_normal_error:
mov ah,40h
mov dx,si
int 21h
mov ah,40h
mov bx,1
mov cx,2
lea dx,newline
int 21h
ret

newline db 0dh,0ah
test_0 dw 0,1
       db "0"
test_1 dw 1,1
       db "1"
test_32767 dw 32767,5
       db "32767"

end start

