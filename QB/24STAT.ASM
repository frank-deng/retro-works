;How to compile:
;TASM 24STAT
;TLINK /t /x 24STAT
;REN 24STAT.COM 24STAT.BIN
.model tiny
MAX_GOAL EQU 99
MAP_ROW_SIZE EQU 256
MAP_SIZE EQU (MAX_GOAL+1)*MAP_ROW_SIZE
.8086
code segment
org 100h
assume cs:code
start:
db 0fdh
dw 0
dw 100h
dw endcode-startcode
startcode:
;a=+18 b=+16 c=+14 d=+12 mmap=+10 pmap=+8 smap=+6 
push bp
mov bp,sp
push ax
push bx
push cx
push dx
push si
push di
push ds
mov ax,[bp+6]
mov ds,ax
push [bp+8]
push [bp+10]
push [bp+12]
push [bp+14]
push [bp+16]
push [bp+18]
mov cx,64
loop_oper:
mov dx,cx
dec dx
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
push dx
call enum_expr
loop loop_oper
add sp,12
pop ds
pop di
pop si
pop dx
pop cx
pop bx
pop ax
mov sp,bp
pop bp
retf 14

;pidx=+20 midx=+18 a=+16 b=+14 c=+12 d=+10 s0=+8 s1=+6 s2=+4
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
call expr_abcsdss
call write_res
call expr_abcssds
call write_res
call expr_abscsds
call write_res
call expr_abscdss
call write_res
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
cmp ax,0
jl write_res_end
cmp ax,MAX_GOAL
jg write_res_end
mov ah,al
xor al,al
mov bx,word ptr[bp+20]
add bx,ax
mov ax,word ptr[bp+18]
or word ptr[bx],ax
write_res_end:
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
cmp si,1
je frac_sub
cmp si,2
je frac_mul
cmp si,3
je frac_div
jmp frac_add

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

endcode:
db 1ah
code ends
end start

