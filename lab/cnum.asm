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
;add al,'0'
stosb
skip_digit:
loop loop_str
mov cx,bx

mov ah,40h
mov bx,1
lea dx,[src_buf]
int 21h

mov ax, 4C00h
int 21h
parsecmd_fail:
mov ah,09h
lea dx,[invalid_input_str]
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

num_str db "¡„“º∑°»˛À¡ŒÈ¬Ω∆‚∞∆æ¡ ∞∞€«™ÕÚ“⁄"
invalid_input_str db "Invalid input$"
src_buf:
end start

