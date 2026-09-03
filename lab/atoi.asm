.8086
.model small
include common.inc
extrn atoui:cPType
.code
public atoi
atoi proc cPType
push cx
push si
cmp byte ptr es:[si],'-'
je atoi_neg
call atoui
jc atoi_error
cmp ax,07fffh
ja atoi_error
cld
jmp atoi_finish
atoi_neg:
inc si
dec cx
call atoui
jc atoi_error
cmp ax,08000h
ja atoi_error
neg ax
cld
atoi_finish:
pop si
pop cx
ret
atoi_error:
xor ax,ax
std
jmp atoi_finish
atoi endp
end

