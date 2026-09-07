.8086
.model small
include common.inc
extrn hextable
.code
public uitox
uitox proc cPType
push ax
push bx
push cx
push ds
mov cx,ax
shr cx,1
shr cx,1
shr cx,1
shr cx,1
and ax,0f0fh
and cx,0f0fh
xchg ah,cl
mov bx,cs
mov ds,bx
lea bx,[hextable]
xlat
xchg ah,al
xlat
xchg cx,ax
xlat
xchg ah,al
xlat
mov es:[di],ax
mov es:[di+2],cx
pop ds
pop cx
pop bx
pop ax
ret
uitox endp
end

