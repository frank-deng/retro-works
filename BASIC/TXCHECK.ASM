-a
org 100h
push ax
push bx
push si
mov si,0
cs:
mov word ptr [si],0
mov ax,db00
int 2fh
cmp al,ff
jnz 100 ;(后面再改)
cmp bx,5450
jnz 100 ;(后面再改)
mov ax,11
int 79h
jnz 100 ;(后面再改)
cs:
mov word ptr [si],1
pop si ;(jnz 100对应的地址改为此处地址)
pop bx
pop ax
retf

org 112
jnz 126
org 118
jnz 126
org 11f
jnz 126
^c
-n txcheck.bin
-rcx
2a
-w

-a
org 100h
push ax
push bx
push si
mov si,0
cs:
mov word ptr [si],0
mov ax,db00
int 2fh
cmp al,ff
jnz 100 ;(后面再改)
cmp bx,5450
jnz 100 ;(后面再改)
mov ax,1
int 79h
jnz 100 ;(后面再改)
mov ax,ff0b
int 16h
cs:
mov word ptr [si],1
pop si
pop bx
pop ax
retf

org 112
jnz 12b
org 118
jnz 12b
org 11f
jnz 12b
^C
-n chk.bin
-rcx
2f
-w

-a
org 100h
push ds
push es
push si
push di
push ax
push bx
mov si,0
mov di,0
mov ax,0
mov bx,0
mov ds,ax
mov es,bx
int 7eh
pop bx
pop ax
pop di
pop si
pop es
pop ds
retf
^C
-n hz.bin
-rcx
1f
-w

