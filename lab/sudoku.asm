;tasm 24solve.asm, 24solve.obj
;tlink /t 24solve.obj, 24solve.com
.8086
PRINT_MAP_BUF_SIZE EQU 200
CellInfo STRUC
  MAP DW ?
  GRP DB ?
  X DB ?
  Y DB ?
  ALIGN 2
CellInfo ENDS
.model tiny
.code
org 100h
start:
call init_map
call print_map
mov ax,04c00h
int 21h
error_dupnum:
mov ah,09h
lea dx,[dupnum_str]
int 21h
mov ax,04c01h
int 21h

print_map:
push bp
mov bp,sp
sub sp,PRINT_MAP_BUF_SIZE
push ax
push bx
push cx
push dx
push si
push di
cld
lea di,[bp-PRINT_MAP_BUF_SIZE]
lea si,[board]
xor dx,dx
print_map_loop_y:
xor dl,dl
print_map_loop_x:
lodsb
add al,'0'
stosb
cmp dl,8
jae print_map_no_space
mov al,' '
stosb
cmp dl,2
je print_map_extra_space
cmp dl,5
je print_map_extra_space
jmp print_map_no_space
print_map_extra_space:
stosb
print_map_no_space:
inc dl
cmp dl,9
jb print_map_loop_x
mov ax,0a0dh
stosw
cmp dh,2
je print_map_extra_line
cmp dh,5
je print_map_extra_line
jmp print_map_no_extra_line
print_map_extra_line:
stosw
print_map_no_extra_line:
inc dh
cmp dh,9
jb print_map_loop_y
mov ax,0a0dh
stosw
lea dx,[bp-PRINT_MAP_BUF_SIZE]
mov cx,di
sub cx,dx
mov bx,1
mov ah,40h
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

init_map:
push bp
mov bp,sp
push ax
push bx
push cx
push dx
push si
push di
lea di,[xygmaps]
mov cx,27
xor ax,ax
cld
rep stosw
xor si,si
xor bx,bx
xor ah,ah
init_map_loop_y:
xor al,al
init_map_loop_x:
mov ch,byte ptr[group_map+si]
mov cl,byte ptr[board+si]
test cl,cl
jz init_map_zero_cell
mov di,1
shl di,cl
mov dx,di
mov bl,ah
shl bx,1
and dx,word ptr[bx+ymap]
jnz init_map_dup
or word ptr[bx+ymap],di
mov dx,di
mov bl,al
shl bx,1
and dx,word ptr[bx+xmap]
jnz init_map_dup
or word ptr[bx+xmap],di
mov dx,di
mov bl,ch
shl bx,1
and dx,word ptr[bx+gmap]
jnz init_map_dup
or word ptr[bx+gmap],di
inc si
init_map_zero_cell:
inc al
cmp al,9
jbe init_map_loop_x
inc ah
cmp ah,9
jbe init_map_loop_y
clc
init_map_end:
pop di
pop si
pop dx
pop cx
pop bx
pop ax
mov sp,bp
pop bp
ret
init_map_dup:
stc
jmp init_map_end

solve1:
push bp
mov bp,sp
push ax
push bx
push cx
push dx
push si
push di

solve1_proc:

pop di
pop si
pop dx
pop cx
pop bx
pop ax
mov sp,bp
pop bp
ret

dupnum_str db "Duplicated number detected.",0dh,0ah,'$'
ALIGN 2
group_map:
db 0,0,0,1,1,1,2,2,2
db 0,0,0,1,1,1,2,2,2
db 0,0,0,1,1,1,2,2,2
db 3,3,3,4,4,4,5,5,5
db 3,3,3,4,4,4,5,5,5
db 3,3,3,4,4,4,5,5,5
db 6,6,6,7,7,7,8,8,8
db 6,6,6,7,7,7,8,8,8
db 6,6,6,7,7,7,8,8,8
ALIGN 2
board:
db 0,1,0,0,0,5,3,9,0
db 5,0,2,0,0,0,0,0,8
db 9,0,0,1,3,0,0,5,0
db 8,0,0,0,4,0,5,0,0
db 0,0,3,5,6,8,7,0,0
db 0,0,1,0,2,0,0,0,9
db 0,8,0,0,5,7,0,0,4
db 1,0,0,0,0,0,2,0,3
db 0,7,9,3,0,0,0,8,0
ALIGN 2
xygmaps:
xmap dw 9 dup(?)
ymap dw 9 dup(?)
gmap dw 9 dup(?)
cell_info:
end start

