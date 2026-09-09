.8086
NUM_MAX EQU 13
NUM_MIN EQU 1
GOAL_MAX EQU 99
GOAL_MIN EQU 0
.model tiny
.code
org 100h
start:
call parsecmd
jc help_info

mov cx,4
lea bx,[nums]
show_loop:
mov ax,[bx]
call show_num
inc bx
inc bx
loop show_loop
mov ax,[goal]
shr ax,1
call show_num

do_exit:
mov ax, 4C00h
int 21h

help_info:
mov ah,09h
lea dx,[help_info_str]
int 21h
jmp do_exit

parsecmd:
push ax
push bx
push cx
push dx
push si
push di
xor ch,ch
mov cl,es:[80h]
mov di,81h
lea bx,[nums]
loop_nums:
call getcmditem
cmp si,di
je parsecmd_fail
push cx
mov cx,di
sub cx,si
call str2num
pop cx
jc parsecmd_fail
mov [bx],ax
inc bx
inc bx
cmp bx,offset nums_end
jb loop_nums
call getcmditem
cmp si,di
je parsecmd_defgoal
mov cx,di
sub cx,si
call str2num
jc parsecmd_fail
mov [goal],ax
parsecmd_defgoal:
clc
parsecmd_end:
pop di
pop si
pop dx
pop cx
pop bx
pop ax
ret
parsecmd_fail:
stc
jmp parsecmd_end

getcmditem:
push ax
jcxz getcmditem_empty
mov al,' '
cld
repe scasb
je getcmditem_empty
dec di
inc cx
mov si,di
repne scasb
jne getcmditem_end
dec di
inc cx
getcmditem_end:
pop ax
ret
getcmditem_empty:
mov si,di
jmp getcmditem_end

str2num:
jcxz str2num_fail
cmp cx,2
ja str2num_fail
jb str2num_onedigit
mov ax,word ptr[si]
sub ax,03030h
cmp ah,9
ja str2num_fail
cmp al,9
ja str2num_fail
xchg ah,al
aad
jmp str2num_fin
str2num_onedigit:
mov al,byte ptr[si]
sub al,030h
cmp al,9
ja str2num_fail
str2num_fin:
xor ah,ah
clc
ret
str2num_fail:
stc
ret

num2str:
push ax
aam
test ah,ah
jz num2str_onedigit
xchg ah,al
or ax,03030h
mov word ptr[di],ax
mov cx,2
jmp num2str_end
num2str_onedigit:
or al,30h
mov byte ptr[di],al
mov cx,1
num2str_end:
pop ax
ret

show_num:
push bp
mov bp,sp
sub sp,2
push ax
push bx
push cx
push dx
push di
lea di,[bp-2]
call num2str
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
new_line_str db '&',0dh,0ah,'$'
end start

