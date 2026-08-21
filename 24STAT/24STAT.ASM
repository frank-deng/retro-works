.model tiny
.8086
assume cs:code,ds:code,es:code,ss:code
code segment
org 100h
start:
;Check file exists
mov ah,4eh
xor cx,cx
lea dx,fname
int 21h
jnc file_exists

;Create file
mov ah,3ch
xor cx,cx
lea dx,fname
int 21h
jc file_create_fail
mov [fhandle],ax

;Init map with zero
mov cx,12800
xor ax,ax
mov di,offset map
rep stosw

call enum_nums
mov ah,40h
mov cx,2
lea dx,text_newline
int 21h
call get_res

end_24stat:
mov bx,[fhandle]
cmp bx,0ffffh
je skip_close_file
mov ah,3eh
int 21h
skip_close_file:
mov ax, 4C00h
int 21h

file_exists:
mov bx,1
mov ah,40h
mov cx,fname_end-fname
lea dx,fname
int 21h
mov ah,40h
mov cx,text_file_exists_end-text_file_exists
lea dx,text_file_exists
int 21h
mov ah,40h
mov cx,2
lea dx,text_newline
int 21h
jmp end_24stat

file_create_fail:
mov bx,1
mov ah,40h
mov cx,text_file_create_fail_end-text_file_create_fail
lea dx,text_file_create_fail
int 21h
mov ah,40h
mov cx,fname_end-fname
lea dx,fname
int 21h
mov ah,40h
mov cx,2
lea dx,text_newline
int 21h
jmp end_24stat

enum_nums:
push bp
mov bp,sp
push ax
push bx
push cx
push dx
push si
push di
xor di,di
call update_progress
mov ax,1
loop_nums0:
mov bx,ax
loop_nums1:
mov cx,bx
loop_nums2:
mov dx,cx
loop_nums3:
push ax
push bx
push cx
push dx
xchg ax,di
call enum_perm_oper
xchg ax,di
inc di
call update_progress
inc dx
cmp dx,13
jle loop_nums3
inc cx
cmp cx,13
jle loop_nums2
inc bx
cmp bx,13
jle loop_nums1
inc ax
cmp ax,13
jle loop_nums0
pop di
pop si
pop dx
pop cx
pop bx
pop ax
pop bp
ret

update_progress:
push bp
mov bp,sp
push ax
push bx
push cx
push dx
push si
push di
mov ah,02h
mov dl,0dh
int 21h
mov ax,di
call int16disp
mov bx,1
mov ah,40h
mov cx,proc_text1_end-proc_text1
lea dx,proc_text1
int 21h
mov ax,di
mov bx,100
mul bx
mov bx,1820
div bx
call int16disp
mov ah,02h
mov dl,'%'
int 21h
pop di
pop si
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
push ax
push bx
push cx
push dx
push si
push di
xor bx,bx
loop_perm:
mov cx,64
loop_oper:
push [bp-2]
xor dx,dx
mov dl,byte ptr[bx+perm]
mov si,dx
shl si,1
mov ax,word ptr [bp+si+4]
push ax
mov dl,byte ptr[bx+perm+1]
mov si,dx
shl si,1
mov ax,word ptr [bp+si+4]
push ax
mov dl,byte ptr[bx+perm+2]
mov si,dx
shl si,1
mov ax,word ptr [bp+si+4]
push ax
mov dl,byte ptr[bx+perm+3]
mov si,dx
shl si,1
mov ax,word ptr [bp+si+4]
push ax

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
loop loop_oper

add bx,4
cmp bx,96
jl loop_perm
pop di
pop si
pop dx
pop cx
pop bx
pop ax
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
ret 16

write_res:
test bx,bx
jz write_res_end
cwd
idiv bx
test dx,dx
jnz write_res_end
cmp ax,0
jl write_res_end
cmp ax,99
jg write_res_end
mov bh,al
mov ax,[bp+18]
mov cl,al
and cl,15
shr ax,1
shr ax,1
shr ax,1
mov bl,al
and bl,0feh
mov ax,08000h
ror ax,cl
or word ptr[bx+map],ax
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

int162str:
push ax
push bx
push dx
push si
push di
xor cx,cx
mov bx,10
mov si,di
or ax,ax
jns int162str_div_loop
neg ax
mov byte ptr es:[di],'-'
inc di
int162str_div_loop:
cwd
div bx
push dx
inc cx
or ax,ax
jnz int162str_div_loop
int162str_store:
pop dx
add dl,'0'
mov byte ptr es:[di],dl
inc di
loop int162str_store
mov cx,di
sub cx,si
pop di
pop si
pop dx
pop bx
pop ax
ret

int16disp:
push bp
mov bp,sp
sub sp,8
push ax
push bx
push cx
push dx
push si
push di
push ds
push es
mov bx,ss
mov ds,bx
mov es,bx
lea di,[bp-8]
call int162str
mov ah,40h
mov bx,1
mov dx,di
int 21h
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

get_res:
push bp
mov bp,sp
sub sp,24
push ax
push bx
push cx
push dx
push si
push di
push ds
push es
mov bx,ss
mov ds,bx
mov es,bx

mov ah,40h
mov bx,[fhandle]
mov cx,text_csv_title_end-text_csv_title
lea dx,text_csv_title
int 21h

xor bx,bx
loop_goal:
xor ah,ah
mov al,bh

lea di,[bp-24]
call int162str
add di,cx
mov byte ptr ss:[di],','
inc di

mov cx,114
xor ax,ax
xor bl,bl
loop_map:
mov dx,[bx+map]
inc bl
inc bl
loop_cnt:
test dx,dx
jz loop_cnt_end
inc ax
mov si,dx
dec dx
and dx,si
jmp loop_cnt
loop_cnt_end:
loop loop_map

call int162str
add di,cx
mov word ptr ss:[di],0a0dh
inc di
inc di

push bx
lea dx,[bp-24]
mov cx,di
sub cx,dx
mov ah,40h
mov bx,[fhandle]
int 21h
pop bx

inc bh
cmp bh,99
jle loop_goal

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

frac_oper_table dw frac_add,frac_sub,frac_mul,frac_div
perm:
db 0,1,2,3, 0,1,3,2, 0,2,1,3, 0,2,3,1, 0,3,1,2, 0,3,2,1
db 1,0,2,3, 1,0,3,2, 1,2,0,3, 1,2,3,0, 1,3,0,2, 1,3,2,0
db 2,0,1,3, 2,0,3,1, 2,1,0,3, 2,1,3,0, 2,3,0,1, 2,3,1,0
db 3,0,1,2, 3,0,2,1, 3,1,0,2, 3,1,2,0, 3,2,0,1, 3,2,1,0
fname db "24STAT.CSV"
fname_end dw 0
text_newline db 0dh,0ah
text_file_exists db " exists, please check."
text_file_exists_end:
text_file_create_fail db "Failed to create output file "
text_file_create_fail_end:
text_csv_title db "Goal,Solvable In 1820",0dh,0ah
text_csv_title_end:
proc_text1 db "/1820 "
proc_text1_end:
fhandle dw 0ffffh

map:
code ends
end start

