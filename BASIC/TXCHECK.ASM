;-a
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
-d 100