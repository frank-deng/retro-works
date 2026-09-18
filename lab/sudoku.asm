;tasm 24solve.asm, 24solve.obj
;tlink /t 24solve.obj, 24solve.com
.8086
PRINT_MAP_BUF_SIZE EQU 200
CellInfo STRUC
  PMAPX DW ?
  PMAPY DW ?
  PMAPGRP DW ?
  PBOARD DW ?
  MAP DW ?
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
;call solve2
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
lea di,[cell_info]
xor si,si
xor bx,bx
xor ah,ah
init_map_loop_y:
xor al,al
init_map_loop_x:
xor dx,dx
mov bx,ax
shl bx,1
xchg bh,dl
add bx,offset xmap
add dx,offset ymap
push bx
push dx
xor bh,bh
mov bl,byte ptr[group_map+si]
shl bl,1
add bx,offset gmap
push bx
mov cl,byte ptr[board+si]
test cl,cl
jz init_map_zero_cell
mov dx,1
shl dx,cl
mov cx,dx
pop bx
and dx,[bx]
jnz init_map_dup
or [bx],cx
mov dx,cx
pop bx
and dx,[bx]
jnz init_map_dup
or [bx],cx
mov dx,cx
pop bx
and dx,[bx]
jnz init_map_dup
or [bx],cx
jmp init_map_next
init_map_zero_cell:
lea bx,[board+si]
mov [di].PBOARD,bx
pop [di].PMAPGRP
pop [di].PMAPY
pop [di].PMAPX
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
push ax
push bx
push cx
push dx
push si
push di
xor ch,ch
mov dx,[cell_info_count]
solve1_proc:
mov cl,dl
xor dx,dx
jcxz solve1_proc_end
lea si,[cell_info]
mov di,si
solve1_loop:
mov bx,[si].PMAPY
mov ax,[bx]
mov bx,[si].PMAPX
or ax,[bx]
mov bx,[si].PMAPGRP
or ax,[bx]
not ax
and ax,03feh
jz solve1_noans
mov bx,ax
dec bx
and bx,ax
jnz update_cellinfo
mov bx,[si].PMAPY
or [bx],ax
mov bx,[si].PMAPX
or [bx],ax
mov bx,[si].PMAPGRP
or [bx],ax
call ctz
mov bx,[si].PBOARD
mov byte ptr[bx],al
add si,SIZE CellInfo
mov dh,1
jmp solve1_loop_next
update_cellinfo:
mov ax,[si].PMAPX
mov [di].PMAPX,ax
mov ax,[si].PMAPY
mov [di].PMAPY,ax
mov ax,[si].PMAPGRP
mov [di].PMAPGRP,ax
mov ax,[si].PBOARD
mov [di].PBOARD,ax
add si,SIZE CellInfo
add di,SIZE CellInfo
inc dl
solve1_loop_next:
loop solve1_loop
test dh,dh
jz solve1_proc_end
jmp solve1_proc
solve1_proc_end:
xor dh,dh
mov [cell_info_count],dx
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


solve2:
push bp
mov bp,sp
sub sp,2
push ax
push bx
push cx
push dx
push si
push di
mov cx,[cell_info_count]
lea si,[cell_info]
init_solve2_loop:
mov bx,[si].PMAPX
mov ax,[bx]
mov bx,[si].PMAPY
or ax,[bx]
mov bx,[si].PMAPGRP
or ax,[bx]
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

mov di,[cell_info_count]
shl di,1
add di,offset stack_area
mov [bp-2],di
solve2_proc:
call get_min_cell
jc solve2_skip_push
push di
solve2_skip_push:

solve2_proc_inner:

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
pop bp
ret
solve2_noans:
stc
jmp solve2_exit

get_min_cell:
push bp
mov bp,sp
push ax
push bx
push cx
push dx
push si
lea si,[cell_info]
mov cl,byte ptr[cell_info_count]
mov ch,0ffh
get_min_cell_loop:
mov bx,[si].PBOARD
cmp byte ptr[bx],0
jnz get_min_cell_continue
mov bx,[si].PMAPX
mov ax,[bx]
mov bx,[si].PMAPX
or ax,[bx]
mov bx,[si].PMAPGRP
or ax,[bx]
not ax
and ax,[si].MAP
jz get_min_cell_fail
xor bl,bl
get_min_cell_count_elem:
inc bl
mov dx,ax
dec dx
and ax,dx
jnz get_min_cell_count_elem
cmp bl,ch
jge get_min_cell_continue
mov ch,bl
mov di,si
get_min_cell_continue:
add si,SIZE CellInfo
dec cl
jnz get_min_cell_loop
clc
get_min_cell_end:
pop si
pop dx
pop cx
pop bx
pop ax
mov sp,bp
pop bp
ret
get_min_cell_fail:
stc
jmp get_min_cell_end


dupnum_str db "Duplicated number detected.",0dh,0ah,'$'
noans_str db "No answer.",0dh,0ah,'$'
ALIGN 2
cell_info_count dw 0
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
db 0,1,0,0,0,5,3,9,0
db 5,0,2,0,0,0,0,0,8
db 9,0,0,1,3,0,0,5,0
db 8,0,0,0,4,0,5,0,0
db 0,0,3,5,6,8,7,0,0
db 0,0,1,0,2,0,0,0,9
db 0,8,0,0,5,7,0,0,4
db 1,0,0,0,0,0,2,0,3
db 0,7,9,3,0,0,0,8,0

;b 0,8,5,0,0,0,0,0,0
;b 0,0,4,0,7,0,0,0,9
;b 0,0,0,0,0,0,0,0,0
;b 3,0,0,0,0,0,0,2,0
;b 7,0,0,0,4,0,0,0,0
;b 0,0,0,1,0,0,0,8,0
;b 0,0,0,2,0,0,0,0,0
;b 9,0,3,0,0,0,0,0,7
;b 0,0,0,8,0,5,0,0,0
ALIGN 2
xygmaps:
xmap dw 9 dup(?)
ymap dw 9 dup(?)
gmap dw 9 dup(?)
xygmaps_end:
cell_info db 81*(SIZE CellInfo) dup(?)
stack_area dw 81 dup(?)
end start 

