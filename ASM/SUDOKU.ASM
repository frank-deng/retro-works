;tasm sudoku.asm, sudoku.obj
;tlink /t sudoku.obj, sudoku.com
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
xor ch,ch
mov cl,es:[80h]
mov di,81h
call getcmditem
cmp si,di
je error_file
lea bx,[board]
push bx
call read_sudoku_file
jc error_file

call getcmditem
cmp si,di
je skip_jigsaw
lea bx,[group_map]
push bx
call read_sudoku_file
jc error_file
call init_jigsaw
jc error_jigsaw
inc byte ptr[jigsaw_enabled]
skip_jigsaw:

call init_map
jc error_dupnum
call solve1
jc no_answer
cmp [cell_info_count],0
je sudoku_finished
call init_solve2
call solve2
jc no_answer
sudoku_finished:
lea si,[board]
call print_map
mov ax,04c00h
int 21h
no_answer:
lea dx,[noans_str]
jmp error_exit
error_dupnum:
lea dx,[dupnum_str]
jmp error_exit
error_jigsaw:
lea dx,[jigsaw_error_str]
jmp error_exit
error_file:
lea dx,[file_error_str]
error_exit:
mov ah,09h
int 21h
mov ax,04c01h
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
jne print_map_no_space
print_map_extra_space:
cmp byte ptr[jigsaw_enabled],0
jne print_map_no_space
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
jne print_map_no_extra_line
print_map_extra_line:
cmp byte ptr[jigsaw_enabled],0
jne print_map_no_extra_line
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
ret 2

ctz:
push ax
xor cl,cl
test al,al
jnz ctz8
mov cl,8
mov al,ah
ctz8:
shr al,1
jc ctz8_end
inc cl
jmp ctz8
ctz8_end:
pop ax
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
mov bx,[si].PBOARD
mov ch,cl
call ctz
mov byte ptr[bx],cl
mov cl,ch
xor ch,ch
add si,SIZE CellInfo
inc dh
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

init_solve2:
push ax
push bx
push cx
push di
mov cx,[cell_info_count]
lea di,[cell_info]
init_solve2_loop:
mov bx,[di].PMAPX
mov ax,[bx]
mov bx,[di].PMAPY
or ax,[bx]
mov bx,[di].PMAPGRP
or ax,[bx]
not ax
and ax,03feh
mov [di].MAP,ax
add di,SIZE CellInfo
loop init_solve2_loop
lea di,[xygmaps]
mov cx,(xygmaps_end-xygmaps)/2
xor ax,ax
cld
rep stosw
pop di
pop cx
pop bx
pop ax
ret

solve2:
push bp
push ax
push bx
push cx
push dx
push si
push di
mov bp,sp
push bp
solve2_proc:
call get_min_cell
jc solve2_skip_push
jz solve2_proc_end
push di
solve2_skip_push:
solve2_proc_inner:
mov bp,sp
mov si,[bp]
mov bx,[si].PBOARD
mov cl,[bx]
test cl,cl
jz solve2_skip_write_map
mov ax,1
shl ax,cl
not ax
mov bx,[si].PMAPX
and [bx],ax
mov bx,[si].PMAPY
and [bx],ax
mov bx,[si].PMAPGRP
and [bx],ax
solve2_skip_write_map:
mov bx,[si].PMAPX
mov ax,[bx]
mov bx,[si].PMAPY
or ax,[bx]
mov bx,[si].PMAPGRP
or ax,[bx]
not ax
and ax,[si].MAP
mov dx,2
shl dx,cl
dec dx
not dx
and ax,dx
jnz solve2_has_candidate
mov bx,[si].PBOARD
mov byte ptr[bx],0
pop bp
cmp bp,sp
je solve2_noans
jmp solve2_proc_inner
solve2_has_candidate:
call ctz
mov bx,[si].PBOARD
mov [bx],cl
mov ax,1
shl ax,cl
mov bx,[si].PMAPX
or [bx],ax
mov bx,[si].PMAPY
or [bx],ax
mov bx,[si].PMAPGRP
or [bx],ax
jmp solve2_proc
solve2_proc_end:
solve2_clear_stack:
pop bp
cmp bp,sp
jne solve2_clear_stack
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
xor di,di
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
jae get_min_cell_continue
mov ch,bl
mov di,si
get_min_cell_continue:
add si,SIZE CellInfo
dec cl
jnz get_min_cell_loop
clc
test di,di
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

read_sudoku_file:
push bp
mov bp,sp
push ax
push bx
push cx
push dx
push si
push di
mov cx,di
sub cx,si
lea di,[file_buf]
mov dx,di
cld
rep movsb
mov byte ptr[di],0
mov ax,03d00h
int 21h
jc read_sudoku_file_exit
mov bx,ax
mov ah,3fh
mov cx,512
int 21h
jc read_sudoku_file_error
mov cx,ax
mov ah,3eh
int 21h
lea si,[file_buf]
mov di,[bp+4]
xor dx,dx
read_sudoku_loop:
cmp dx,0909h
jae read_sudoku_finish
lodsb
cmp al,0ah
je read_sudoku_next_line
cmp dl,9
jae read_sudoku_loop_continue
cmp al,'.'
jne read_sudoku_solid_cell
xor al,al
jmp read_sudoku_write
read_sudoku_solid_cell:
sub al,'0'
cmp al,9
ja read_sudoku_loop_continue
read_sudoku_write:
stosb
inc dl
jmp read_sudoku_loop_continue
read_sudoku_next_line:
test dl,dl
jz read_sudoku_loop_continue
xor dl,dl
inc dh
read_sudoku_loop_continue:
loop read_sudoku_loop
read_sudoku_finish:
clc
read_sudoku_file_exit:
pop di
pop si
pop dx
pop cx
pop bx
pop ax
mov sp,bp
pop bp
ret 2
read_sudoku_file_error:
mov ah,3eh
int 21h
stc
jmp read_sudoku_file_exit

init_jigsaw:
push bp
mov bp,sp
sub sp,10
push ax
push bx
push cx
push dx
push si
push di
lea di,[bp-10]
mov cx,5
xor ax,ax
cld
rep stosw
lea si,[group_map]
mov cx,81
xor ah,ah
cld
init_jigsaw_loop:
dec byte ptr[si]
lodsb
cmp al,8
ja init_jigsaw_fail
mov di,ax
inc byte ptr[bp+di-10]
loop init_jigsaw_loop
lea si,[bp-10]
mov cx,9
mov al,9
cld
repe scasb
jz init_jigsaw_fail
clc
init_jigsaw_exit:
pop di
pop si
pop dx
pop cx
pop bx
pop ax
mov sp,bp
pop bp
ret
init_jigsaw_fail:
stc
jmp init_jigsaw_exit

file_error_str db "Failed to read file.",0dh,0ah,'$'
jigsaw_error_str db "Invalid jigsaw data.",0dh,0ah,'$'
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
jigsaw_enabled db 0
board db 82 dup(?)
file_buf:
xygmaps:
xmap dw 9 dup(?)
ymap dw 9 dup(?)
gmap dw 9 dup(?)
xygmaps_end:
cell_info db 81*(SIZE CellInfo) dup(?)
end start 

