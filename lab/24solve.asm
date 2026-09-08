.8086
NUM_MAX EQU 13
NUM_MIN EQU 1
GOAL_MAX EQU 99
GOAL_MIN EQU 0
.model tiny
include cmdline.inc
extrn atoui:cPType
extrn uitoa:cPType
.code
org 100h
start:
cmdinit
lea bx,[nums]
loop_nums:
call cmdparse
mov dx,di
sub dx,si
jz help_info
xchg dx,cx
call atoui
jc help_info
cmp ax,NUM_MAX
jg help_info
cmp ax,NUM_MIN
jl help_info
xchg dx,cx
mov [bx],ax
inc bx
inc bx
cmp bx,offset nums_end
jb loop_nums

call cmdparse
mov cx,di
sub cx,si
jz default_goal
call atoui
jc help_info
cmp ax,GOAL_MAX
ja help_info
mov word ptr[goal],ax
default_goal:

mov cx,4
lea bx,[nums]
show_loop:
mov ax,[bx]
call show_num
inc bx
inc bx
loop show_loop
mov ax,[goal]
call show_num

do_exit:
mov ax, 4C00h
int 21h

help_info:
mov ah,09h
lea dx,[help_info_str]
int 21h
jmp do_exit

show_num:
push bp
mov bp,sp
sub sp,8
push ax
push bx
push cx
push dx
push di
lea di,[bp-8]
call uitoa
mov ah,40h
mov bx,1
mov dx,di
int 21h
mov ah,09h
lea dx,[new_line_str]
int 21h
pop di
pop dx
pop cx
pop bx
pop ax
mov sp,bp
pop bp
ret

nums dw 4 dup(0)
nums_end:
goal dw 24
help_info_str db "Usage: 24SOLVE a b c d [Goal]",0dh,0ah
db "    Goal defaults to 24 if not provided",0dh,0ah,'$'
new_line_str db 0dh,0ah,'$'
end start

