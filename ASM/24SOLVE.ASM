;tasm 24solve.asm, 24solve.obj
;tlink /t 24solve.obj, 24solve.com
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

;Enumerate perm and oper
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
jc found_answer
loop loop_oper
skip_perm:
add sp,8
add bx,4
cmp bx,96
jb loop_perm
mov ah,09h
lea dx,[no_answer_str]
int 21h
found_answer:
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
inc di
inc di
jmp num2str_end
num2str_onedigit:
or al,30h
mov byte ptr[di],al
inc di
num2str_end:
pop ax
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

print_expr:
test bx,bx
jz check_res_fail
cwd
idiv bx
test dx,dx
jnz check_res_fail
cmp ax,[goal]
jne check_res_fail
lea bx,[opers_str]
push [goal]
push [bp+10]
mov ax,[bp+4]
xlat
push ax
push [bp+12]
mov ax,[bp+6]
xlat
push ax
push [bp+14]
mov ax,[bp+8]
xlat
push ax
push [bp+16]
lea di,[output_buf]
call format_str
add sp,16
mov dx,di
mov ah,09h
int 21h
stc
ret
check_res_fail:
clc
ret

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
jc enum_expr_finish
call expr_abcsdss
jc enum_expr_finish
call expr_abcssds
jc enum_expr_finish
call expr_abscsds
jc enum_expr_finish
call expr_abscdss
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

expr_abcdsss: ;n#(n#(n#n))
mov ax,word ptr[bp+12]
mov bx,1
mov cx,word ptr[bp+10]
mov dx,1
mov si,word ptr[bp+4]
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
mov si,word ptr[bp+8]
call frac_oper
lea si,[expr_str_abcdsss]
jmp print_expr

expr_abcsdss: ;n#((n#n)#n)
mov ax,word ptr[bp+14]
mov bx,1
mov cx,word ptr[bp+12]
mov dx,1
mov si,word ptr[bp+6]
call frac_oper
mov cx,word ptr[bp+10]
mov dx,1
mov si,word ptr[bp+4]
call frac_oper
mov cx,ax
mov dx,bx
mov ax,word ptr[bp+16]
mov bx,1
mov si,word ptr[bp+8]
call frac_oper
lea si,[expr_str_abcsdss]
jmp print_expr

expr_abcssds: ;(n#(n#n))#n
mov ax,word ptr[bp+14]
mov bx,1
mov cx,word ptr[bp+12]
mov dx,1
mov si,word ptr[bp+6]
call frac_oper
mov cx,ax
mov dx,bx
mov ax,word ptr[bp+16]
mov bx,1
mov si,word ptr[bp+8]
call frac_oper
mov cx,word ptr[bp+10]
mov dx,1
mov si,word ptr[bp+4]
call frac_oper
lea si,[expr_str_abcssds]
jmp print_expr

expr_abscsds: ;((n#n)#n)#n
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
lea si,[expr_str_abscsds]
jmp print_expr

expr_abscdss: ;(n#n)#(n#n)
mov ax,word ptr[bp+12]
mov bx,1
mov cx,word ptr[bp+10]
mov dx,1
mov si,word ptr[bp+4]
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
mov si,word ptr[bp+6]
call frac_oper
lea si,[expr_str_abscdss]
jmp print_expr

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

format_str:
push bp
mov bp,sp
push ax
push bx
push cx
push dx
push si
push di
cld
lea bx,[bp+4]
format_str_loop:
lodsb
cmp al,'n'
je format_str_num
cmp al,'#'
je format_str_char
stosb
cmp al,'$'
jne format_str_loop
jmp format_str_end
format_str_char:
mov ax,ss:[bx]
inc bx
inc bx
stosb
jmp format_str_loop
format_str_num:
mov ax,ss:[bx]
inc bx
inc bx
call num2str
jmp format_str_loop
format_str_end:
pop di
pop si
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
no_answer_str db "No answer.",0dh,0ah,'$'
opers_str db "+-*/"
expr_str_abcdsss db "n#(n#(n#n))=n",0dh,0ah,'$'
expr_str_abcsdss db "n#((n#n)#n)=n",0dh,0ah,'$'
expr_str_abcssds db "(n#(n#n))#n=n",0dh,0ah,'$'
expr_str_abscsds db "((n#n)#n)#n=n",0dh,0ah,'$'
expr_str_abscdss db "(n#n)#(n#n)=n",0dh,0ah,'$'
frac_oper_table dw frac_add,frac_sub,frac_mul,frac_div
perm:
db 0,1,2,3, 0,1,3,2, 0,2,1,3, 0,2,3,1, 0,3,1,2, 0,3,2,1
db 1,0,2,3, 1,0,3,2, 1,2,0,3, 1,2,3,0, 1,3,0,2, 1,3,2,0
db 2,0,1,3, 2,0,3,1, 2,1,0,3, 2,1,3,0, 2,3,0,1, 2,3,1,0
db 3,0,1,2, 3,0,2,1, 3,1,0,2, 3,1,2,0, 3,2,0,1, 3,2,1,0
hash_map:
output_buf:
end start

