.8086
.model small
include common.inc
.code
public cmdparse
cmdparse proc cPType
push ax
jcxz cmdparse_empty
mov al,' '
cld
repe scasb
je cmdparse_empty
dec di
inc cx
mov si,di
repne scasb
jne cmdparse_end
dec di
inc cx
cmdparse_end:
test si,di
pop ax
ret
cmdparse_empty:
mov si,di
jmp cmdparse_end
cmdparse endp
end

