.8086
.model small
include common.inc
.code
public atoui
atoui proc cPType
push bx
push cx
push dx
push si
push di
push ds
mov di,10
mov ax,es
mov ds,ax
xor ax,ax
xor bx,bx
atoui_loop:
xchg bx,ax
lodsb
sub al,'0'
cmp al,9
ja atoui_error
xchg bx,ax
mul di
test dx,dx
jc atoui_error
add ax,bx
jc atoui_error
loop atoui_loop
cld
atoui_finish:
pop ds
pop di
pop si
pop dx
pop cx
pop bx
ret
atoui_error:
xor ax,ax
std
jmp atoui_finish
atoui endp
end

