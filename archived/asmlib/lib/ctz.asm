.8086
.model small
include common.inc
.code
public ctz
ctz proc cPType
test ax,ax
jz all_zero
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
all_zero:
stc
ret
ctz endp
end

