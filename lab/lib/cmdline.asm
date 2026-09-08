.8086
.model small
include common.inc
.code
public cmdparse
cmdparse proc cPType
mov si,di
jcxz empty_str
push ax
push ds
mov ax,es
mov ds,ax
mov al,' '
cld
repe scasb
je cmdparse_end
dec di
inc cx
mov si,di
repne scasb
jne cmdparse_end
dec di
inc cx
cmdparse_end:
pop ds
pop ax
empty_str:
ret
cmdparse endp
end

