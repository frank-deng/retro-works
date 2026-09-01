s16toa_inc proc
push ax
push bx
push dx
push si
push di
xor cx,cx
mov si,di
or ax,ax
jns int162str_proc
neg ax
mov byte ptr [di],'-'
inc di
int162str_proc:
cmp ax,10
jl int162str_10
cmp ax,100
jl int162str_100
cmp ax,1000
jl int162str_1000
cmp ax,10000
jl int162str_10000
cwd
mov bx,10000
div bx
add al,'0'
mov byte ptr[di],al
inc di
mov ax,dx
int162str_10000:
cwd
mov bx,1000
div bx
add al,'0'
mov byte ptr[di],al
inc di
mov ax,dx
int162str_1000:
cwd
mov bx,100
div bx
add al,'0'
mov byte ptr[di],al
inc di
mov ax,dx
int162str_100:
aam
add ah,'0'
mov byte ptr[di],ah
inc di
int162str_10:
add al,'0'
mov byte ptr[di],al
inc di
mov cx,di
sub cx,si
pop di
pop si
pop dx
pop bx
pop ax
ret
s16toa_inc endp
