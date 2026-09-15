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
jc error_dupnum
call solve1
jc no_answer
cmp [cell_info_count],0
je sudoku_finished
call solve2
sudoku_finished:
call print_map

mov ax,04c00h
int 21h
no_answer:
mov ah,09h
lea dx,[noans_str]
int 21h
mov ax,04c01h
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

ctz:
test ax,ax
jz ctz_all_zero
push cx
xor cl,cl
test al,al
jnz ctz8
mov cl,8
mov al,ah
ctz8:
inc cl
shr al,1
jnc ctz8
dec cl
xor ah,ah
mov al,cl
pop cx
clc
ret
ctz_all_zero:
stc
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
mov cx,(xygmaps_end-xygmaps)/2
xor ax,ax
cld
rep stosw
mov word ptr[cell_info_count],0
lea di,[cell_info]
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
push di
mov dx,1
shl dx,cl
mov di,dx
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
pop di
jmp init_map_next
init_map_zero_cell:
mov byte ptr[di].X,al
mov byte ptr[di].Y,ah
mov byte ptr[di].GRP,ch
add di,SIZE CellInfo
inc word ptr[cell_info_count]
init_map_next:
inc si
inc al
cmp al,9
jb init_map_loop_x
inc ah
cmp ah,9
jb init_map_loop_y
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
sub sp,6
push ax
push bx
push cx
push dx
push si
push di
solve1_proc:
xor dl,dl
mov cx,[cell_info_count]
jcxz solve1_proc_end
mov [cell_info_count],0
lea si,[cell_info]
mov di,si
solve1_loop:
call solve1_get_candidate
jz solve1_noans
mov bx,ax
dec bx
and bx,ax
jnz update_cellinfo
mov bx,[bp-2]
or [bx+ymap],ax
mov bx,[bp-4]
or [bx+xmap],ax
mov bx,[bp-6]
or [bx+gmap],ax
mov bl,[si].Y
mov bh,bl
shl bl,1
shl bl,1
shl bl,1
add bl,bh
add bl,[si].X
xor bh,bh
call ctz
mov byte ptr[board+bx],al
add si,SIZE CellInfo
mov dl,1
jmp solve1_loop_next
update_cellinfo:
mov ax,[si]
mov [di],ax
mov ax,[si+2]
mov [di+2],ax
mov ax,[si+4]
mov [di+4],ax
add si,SIZE CellInfo
add di,SIZE CellInfo
inc [cell_info_count]
solve1_loop_next:
loop solve1_loop
test dl,dl
jnz solve1_proc
solve1_proc_end:
cld
solve1_exit:
pop di
pop si
pop dx
pop cx
pop bx
pop ax
mov sp,bp
pop bp
ret
solve1_noans:
stc
jmp solve1_exit

solve1_get_candidate:
xor bh,bh
mov bl,[si].Y
shl bx,1
mov [bp-2],bx
mov ax,[bx+ymap]
mov bl,[si].X
shl bx,1
mov [bp-4],bx
or ax,[bx+xmap]
mov bl,[si].GRP
shl bx,1
mov [bp-6],bx
or ax,[bx+gmap]
not ax
and ax,03feh
ret

solve2:
push bp
mov bp,sp
push ax
push bx
push cx
push dx
push si
push di
mov cx,[cell_info_count]
lea si,[cell_info]
init_solve2_loop:
xor bh,bh
mov bl,byte ptr[si].X
shl bl,1
mov ax,[xmap+bx]
mov bl,byte ptr[si].Y
shl bl,1
or ax,[ymap+bx]
mov bl,byte ptr[si].GRP
shl bl,1
or ax,[gmap+bx]
not ax
and ax,03feh
mov word ptr[si].MAP,ax
add si,SIZE CellInfo
loop init_solve2_loop
lea di,[xygmaps]
mov cx,(xygmaps_end-xygmaps)/2
xor ax,ax
cld
rep stosw

mov ax,[cell_info_count]
mov bx,SIZE CellInfo
mul bx
mov di,ax
solve2_proc:
call get_min_cell
jc solve2_skip_push
dec di
dec di
mov [di],bx
solve2_skip_push:
xor ax,ax
solve2_proc_inner:
mov bx,[di]
mov ah,[bx+cell_info].Y
mov al,[bx+cell_info].X
mov ch,[bx+cell_info].GRP
xor bh,bh
mov bl,ah
shl bl,1
shl bl,1
shl bl,1
add bl,ah
add bl,al
mov cl,byte ptr[board+bx]
test cl,cl
jz solve2_skip_wmap1
mov dx,1
shl dx,cl
not dx
xor bh,bh
mov bl,al
shl bl,1
and [bx+xmap],dx
mov bl,ah
shl bl,1
and [bx+ymap],dx
mov bl,ch
shl bl,1
and [bx+gmap],dx
solve2_skip_wmap1:

jmp solve2_proc_inner
cmp di,0
jle solve2_proc
solve2_proc_end:
cld
solve2_exit:
pop di
pop si
pop dx
pop cx
pop bx
pop ax
mov sp,bp
pop bp
ret
solve2_noans:
stc
jmp solve2_exit

get_min_cell:
push bp
mov bp,sp
sub sp,4
push ax
push cx
push dx
push si
lea si,[cell_info]
mov [bp-4],si
mov cx,[cell_info_count]
mov word ptr[bp-2],0ffh
get_min_cell_loop:
mov al,byte ptr[si].X
mov ah,byte ptr[si].Y
xor bh,bh
mov bl,ah
shl bl,1
shl bl,1
shl bl,1
add bl,ah
add bl,al
mov bl,byte ptr[board+bx]
test bl,bl
jz get_min_cell_continue
xor bh,bh
mov bl,al
shl bl,1
mov dx,[xmap+bx]
mov bl,ah
shl bl,1
or dx,[ymap+bx]
mov bl,byte ptr[si].GRP
shl bl,1
or dx,[gmap+bx]
not dx
and dx,word ptr[si].MAP
jz get_min_cell_fail
xor al,al
get_min_cell_count_elem:
inc al
mov bx,dx
dec bx
and dx,bx
jnz get_min_cell_count_elem
cmp al,[bp-2]
jge get_min_cell_continue
mov [bp-2],al
mov [bp-4],si
get_min_cell_continue:
add si,SIZE CellInfo
loop get_min_cell_loop
mov bx,[bp-4]
clc
get_min_cell_end:
pop si
pop dx
pop cx
pop ax
mov sp,bp
pop bp
ret
get_min_cell_fail:
stc
jmp get_min_cell_end

dupnum_str db "Duplicated number detected.",0dh,0ah,'$'
noans_str db "No answer.",0dh,0ah,'$'
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
board:
;b 0,1,0,0,0,5,3,9,0
;b 5,0,2,0,0,0,0,0,8
;b 9,0,0,1,3,0,0,5,0
;b 8,0,0,0,4,0,5,0,0
;b 0,0,3,5,6,8,7,0,0
;b 0,0,1,0,2,0,0,0,9
;b 0,8,0,0,5,7,0,0,4
;b 1,0,0,0,0,0,2,0,3
;b 0,7,9,3,0,0,0,8,0
db 0,8,5,0,0,0,0,0,0
db 0,0,4,0,7,0,0,0,9
db 0,0,0,0,0,0,0,0,0
db 3,0,0,0,0,0,0,2,0
db 7,0,0,0,4,0,0,0,0
db 0,0,0,1,0,0,0,8,0
db 0,0,0,2,0,0,0,0,0
db 9,0,3,0,0,0,0,0,7
db 0,0,0,8,0,5,0,0,0
ALIGN 2
xygmaps:
xmap dw 9 dup(?)
ymap dw 9 dup(?)
gmap dw 9 dup(?)
xygmaps_end:
cell_info_count dw ?
cell_info db 81*(SIZE CellInfo) dup(?)
stack_area dw 81 dup(?)
end start 

