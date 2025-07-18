;How to compile
;wasm -fo=postscr.obj postscr.asm
;wlink NAME postscr.com FILE postscr.obj SYSTEM DOS COM
.model tiny
.8086
assume cs:code,ds:code,es:code,ss:code
code segment
org 100h
start:
push es
mov dx,0xb800
mov es,dx
mov cx,4000
mov bx,0
mov dx,0x0700
cls_loop:
mov es:[bx],dx
add bx,2
loop cls_loop
pop es

print_mem:
mov ah,2
mov dx,0
mov bh,0
int 0x10

mov ax,word ptr [memtracked]
mov bx,10
mov cx,4
getnum:
xor dx,dx
div bx
add dl,'0'
push dx
loop getnum
mov cx,4
printnum:
pop ax
mov ah,0x0e
int 0x10
loop printnum
mov ax,0x1301
mov bx,7
mov cx,offset drvstr0-offset memstr
mov dx,4
mov bp,offset memstr
int 0x10
mov ax,1
call sleep
cmp word ptr [memtracked],640
jge mem_finish
add word ptr [memtracked],16
jmp print_mem

mem_finish:
mov ax,8
call sleep
mov ax,0x1301
mov bx,7
mov dx,0x0305
mov cx,offset drvstr1-offset drvstr0
mov bp,offset drvstr0
int 0x10
mov dx,0x0407
mov cx,offset drvstr2-offset drvstr1
mov bp,offset drvstr1
int 0x10
mov dx,0x0507
mov cx,offset drvstr3-offset drvstr2
mov bp,offset drvstr2
int 0x10
mov dx,0x0605
mov cx,offset drvstrend-offset drvstr3
mov bp,offset drvstr3
int 0x10
mov ah,2
mov dx,0x0800
mov bh,0
int 0x10

in al,0x61
or al,0x3
out 0x61,al
mov al,0xb6
out 0x43,al
mov al,0xf0
out 0x42,al
mov al,0x05
out 0x42,al

mov ax,2
call sleep

in al,0x61
and al,0xFC
out 0x61,al

mov ax,20
call sleep

ret

sleep:
mov word ptr[timer],ax
mov ax,0
int 1ah
mov bx,dx
waitloop:
hlt
mov ax,0
int 1ah
cmp dx,bx
je waitloop
mov bx,dx
dec word ptr[timer]
jnz waitloop
ret

memtracked dw 0
timer dw 0
memstr db "K OK"
drvstr0 db "---- DRIVE TYPE ----"
drvstr1 db "DRIVE A  1.2 MB"
drvstr2 db "DRIVE B  360 KB"
drvstr3 db "--------------------"
drvstrend:

code ends
end start

