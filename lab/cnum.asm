.8086
MAX_LEN EQU 16
.model tiny
.code
org 100h
start:
mov cl,es:[80h]
mov di,81h
call getcmditem
cmp si,di
jne parsecmd_found_item
jmp parsecmd_fail
parsecmd_found_item:
mov cx,di
sub cx,si
cmp cx,MAX_LEN
jbe length_check_passed
jmp parsecmd_fail
length_check_passed:
xor bx,bx
lea di,[src_buf]
loop_str:
lodsb
sub al,'0'
cmp al,9
ja parsecmd_fail
test al,al
jnz normal_num
test bx,bx
jz skip_digit
normal_num:
inc bx
stosb
skip_digit:
loop loop_str
mov cx,bx

lea si,[src_buf]

cmp cx,8
jbe val_1e8
sub cx,8
call proc_1e8
mov ax,14
call disp_val
add si,cx
mov cx,8
val_1e8:
call proc_1e8

lea dx,[newline_str]
mov ah,40h
mov bx,1
mov cx,2
int 21h
mov ax, 4C00h
int 21h
parsecmd_fail:
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

disp_val:
push ax
push bx
push cx
push dx
mov dl,al
xor dh,dh
shl dx,1
add dx,offset num_str
mov ah,40h
mov bx,1
mov cx,2
int 21h
pop dx
pop cx
pop bx
pop ax
ret

proc_1e8:
push ax
push bx
push cx
push dx
push si
push di
mov di,si
xor al,al
cld
repe scasb
je no_disp_1e8
inc cx
dec di
cmp byte ptr[si],0
jne no_leading_zero_1e8
xor ax,ax
call disp_val
no_leading_zero_1e8:
mov si,di
cmp cx,4
jbe val_1e4
sub cx,4
call proc_1e4
mov ax,13
call disp_val
add si,cx
mov cx,4
val_1e4:
call proc_1e4
no_disp_1e8:
pop di
pop si
pop dx
pop cx
pop bx
pop ax
ret

proc_1e4:
push ax
push bx
push cx
push dx
push si
push di
mov di,si
xor al,al
cld
repe scasb
je no_disp_1e4
inc cx
dec di
xor ax,ax
cmp byte ptr[si],0
jne no_leading_zero_1e4
call disp_val
no_leading_zero_1e4:
mov si,di
cmp cx,4
je disp_1e3
cmp cx,3
je disp_1e2
cmp cx,2
je disp_1e1
jmp disp_1e0
disp_1e3:
lodsb
call disp_val
mov ax,12
call disp_val
disp_1e2:
lodsb
test al,al
jz disp_1e1
call disp_val
mov ax,11
call disp_val
mov ah,al
disp_1e1:
lodsb
test ax,ax
jz disp_1e0
test al,al
jnz skip_zero_1e1
call disp_val
skip_zero_1e1:
call disp_val
mov ax,10
call disp_val
disp_1e0:
lodsb
test al,al
jz no_disp_1e4
call disp_val
no_disp_1e4:
pop di
pop si
pop dx
pop cx
pop bx
pop ax
ret

num_str db "¡„“º∑°»˛À¡ŒÈ¬Ω∆‚∞∆æ¡ ∞∞€«™ÕÚ“⁄"
newline_str db 0dh,0ah
src_buf:
end start

