.8086
HASH_MAP_SIZE EQU 4096
MAX_GOAL EQU 99
NUM_MAX EQU 13
NUM_MIN EQU 1
GOAL_MAX EQU 99
GOAL_MIN EQU 0
.model tiny
.code
org 100h
start:
;Parse cmdline
mov cl,es:[80h]
mov di,81h
lea bx,[nums]
parsecmd_loop_nums:
call getcmditem
cmp si,di
jne parsecmd_found_item
jmp parsecmd_fail
parsecmd_found_item:
push cx
mov cx,di
sub cx,si
call str2num
pop cx
jnc parsecmd_item_passed
jmp parsecmd_fail
parsecmd_item_passed:
mov [bx],ax
inc bx
inc bx
cmp bx,offset nums_end
jb parsecmd_loop_nums

call getcmditem
cmp si,di
je parsecmd_defgoal
mov cx,di
sub cx,si
call str2num
jnc parsecmd_goal_passed
jmp parsecmd_fail
parsecmd_goal_passed:
mov [goal],ax
parsecmd_defgoal:

;Clear hash map
xor ax,ax
lea di,[hash_map]
mov cx,HASH_MAP_SIZE/2
cld
rep stosw

call enum_perm_oper

;mov cx,4
;lea bx,[nums]
;show_loop:
;mov ax,[bx]
;call show_num
;inc bx
;inc bx
;loop show_loop
;mov ax,[goal]
;shr ax,1
;call show_num

do_exit:
mov ax, 4C00h
int 21h

parsecmd_fail:
help_info:
mov ah,09h
lea dx,[help_info_str]
int 21h
mov ax, 4C01h
int 21h

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

enum_perm_oper:
push bp
mov bp,sp
push bx
push cx
push dx
push si
push di
push ax
xor bx,bx
loop_perm:
xor dx,dx
mov dl,byte ptr[bx+perm]
mov si,dx
shl si,1
mov ax,word ptr [nums+si]
push ax
mov dl,byte ptr[bx+perm+1]
mov si,dx
shl si,1
mov ax,word ptr [nums+si]
push ax
mov dl,byte ptr[bx+perm+2]
mov si,dx
shl si,1
mov ax,word ptr [nums+si]
push ax
mov dl,byte ptr[bx+perm+3]
mov si,dx
shl si,1
mov ax,word ptr [nums+si]
push ax
call proc_hash
jc skip_perm
mov cx,64
loop_oper:
mov dx,cx
dec dx
and dx,03fh
mov ax,dx
and ax,3
push ax
shr dx,1
shr dx,1
mov ax,dx
and ax,3
push ax
shr dx,1
shr dx,1
mov ax,dx
push ax
call enum_expr
jc enum_perm_oper_end
loop loop_oper
skip_perm:
add sp,8
add bx,4
cmp bx,96
jb loop_perm
enum_perm_oper_end:
pop ax
pop di
pop si
pop dx
pop cx
pop bx
pop bp
ret 8

;idx=+18 a=+16 b=+14 c=+12 d=+10 s0=+8 s1=+6 s2=+4
enum_expr:
push bp
mov bp,sp
push ax
push bx
push cx
push dx
push si
push di
call expr_abcdsss
call write_res
jc enum_expr_finish
call expr_abcsdss
call write_res
jc enum_expr_finish
call expr_abcssds
call write_res
jc enum_expr_finish
call expr_abscsds
call write_res
jc enum_expr_finish
call expr_abscdss
call write_res
enum_expr_finish:
pop di
pop si
pop dx
pop cx
pop bx
pop ax
mov sp,bp
pop bp
ret 6

write_res:
test bx,bx
jz write_res_end
cwd
idiv bx
test dx,dx
jnz write_res_end
cmp ax,[goal]
jne write_res_end
push ax
push dx
mov ah,09h
lea dx,[has_answer]
int 21h
pop dx
pop ax
stc
ret
write_res_end:
clc
ret

expr_abcdsss:
mov ax,word ptr[bp+12]
mov bx,1
mov cx,word ptr[bp+10]
mov dx,1
mov si,word ptr[bp+8]
call frac_oper
mov cx,ax
mov dx,bx
mov ax,word ptr[bp+14]
mov bx,1
mov si,word ptr[bp+6]
call frac_oper
mov cx,ax
mov dx,bx
mov ax,word ptr[bp+16]
mov bx,1
mov si,word ptr[bp+4]
call frac_oper
ret

expr_abcsdss:
mov ax,word ptr[bp+14]
mov bx,1
mov cx,word ptr[bp+12]
mov dx,1
mov si,word ptr[bp+8]
call frac_oper
mov cx,word ptr[bp+10]
mov dx,1
mov si,word ptr[bp+6]
call frac_oper
mov cx,ax
mov dx,bx
mov ax,word ptr[bp+16]
mov bx,1
mov si,word ptr[bp+4]
call frac_oper
ret

expr_abcssds:
mov ax,word ptr[bp+14]
mov bx,1
mov cx,word ptr[bp+12]
mov dx,1
mov si,word ptr[bp+8]
call frac_oper
mov cx,ax
mov dx,bx
mov ax,word ptr[bp+16]
mov bx,1
mov si,word ptr[bp+6]
call frac_oper
mov cx,word ptr[bp+10]
mov dx,1
mov si,word ptr[bp+4]
call frac_oper
ret

expr_abscsds:
mov ax,word ptr[bp+16]
mov bx,1
mov cx,word ptr[bp+14]
mov dx,1
mov si,word ptr[bp+8]
call frac_oper
mov cx,word ptr[bp+12]
mov dx,1
mov si,word ptr[bp+6]
call frac_oper
mov cx,word ptr[bp+10]
mov dx,1
mov si,word ptr[bp+4]
call frac_oper
ret

expr_abscdss:
mov ax,word ptr[bp+12]
mov bx,1
mov cx,word ptr[bp+10]
mov dx,1
mov si,word ptr[bp+6]
call frac_oper
push ax
push bx
mov ax,word ptr[bp+16]
mov bx,1
mov cx,word ptr[bp+14]
mov dx,1
mov si,word ptr[bp+8]
call frac_oper
pop dx
pop cx
mov si,word ptr[bp+4]
call frac_oper
ret

frac_oper:
test bx,bx
jz frac_oper_zero
test dx,dx
jz frac_oper_zero
and si,3
shl si,1
mov si,frac_oper_table[si]
jmp si

frac_oper_zero:
xor ax,ax
xor bx,bx
ret

frac_mul:
xchg ax,bx
imul dx
xchg ax,bx
imul cx
ret

frac_div:
imul dx
xchg ax,bx
imul cx
xchg ax,bx
ret

frac_add:
mov si,ax
mov di,dx
mov ax,cx
imul bx
mov cx,ax
mov ax,bx
imul di
mov bx,ax
mov ax,si
imul di
add ax,cx
ret

frac_sub:
mov si,ax
mov di,dx
mov ax,cx
imul bx
mov cx,ax
mov ax,bx
imul di
mov bx,ax
mov ax,si
imul di
sub ax,cx
ret

proc_hash:
push bp
mov bp,sp
push ax
push bx
push cx
push dx
mov ax,[bp+4]
mov bx,[bp+6]
sub ax,bx
add ax,15
mov dx,[bp+8]
sub bx,dx
add bx,15
sub dx,[bp+10]
add dx,15
shl bx,1
shl bx,1
shl bx,1
shl bx,1
shl bx,1
or bx,ax
shl bx,1
mov ch,dl
shr ch,1
shr ch,1
shr ch,1
shr ch,1
or bl,ch
shl bx,1
mov cl,dl
and cl,0fh
mov ax,08000h
ror ax,cl
mov cx,word ptr[bx+hash_map]
and cx,ax
jnz proc_hash_skip
or word ptr[bx+hash_map],ax
clc
jmp proc_hash_end
proc_hash_skip:
stc
proc_hash_end:
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
has_answer db "ans$"
new_line_str db 0dh,0ah,'$'
frac_oper_table dw frac_add,frac_sub,frac_mul,frac_div
perm:
db 0,1,2,3, 0,1,3,2, 0,2,1,3, 0,2,3,1, 0,3,1,2, 0,3,2,1
db 1,0,2,3, 1,0,3,2, 1,2,0,3, 1,2,3,0, 1,3,0,2, 1,3,2,0
db 2,0,1,3, 2,0,3,1, 2,1,0,3, 2,1,3,0, 2,3,0,1, 2,3,1,0
db 3,0,1,2, 3,0,2,1, 3,1,0,2, 3,1,2,0, 3,2,0,1, 3,2,1,0
hash_map:
end start

