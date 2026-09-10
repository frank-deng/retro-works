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
mov di,10
xor ax,ax
xor bx,bx
cld
atoui_loop:
xchg bx,ax
db 26h,0ach ;es:lodsb
sub al,'0'
cmp al,9
ja atoui_error
xchg bx,ax
mul di
jc atoui_error
add ax,bx
jc atoui_error
loop atoui_loop
clc
atoui_finish:
pop di
pop si
pop dx
pop cx
pop bx
ret
atoui_error:
xor ax,ax
stc
jmp atoui_finish
atoui endp
end

