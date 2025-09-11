;How to compile:
;TASM UTIL
;TLINK /t /x UTIL
;REN UTIL.COM UTIL.BIN
code segment
org 100h
assume cs:code
start:
db 0fdh
dw 0
dw 100h
dw codeend-codestart
codestart:
dw envtest-codestart
dw getcharbitmap-codestart
dw drawbitmap-codestart

envtest:
push bp
mov bp,sp
mov si,[bp+6]
mov word ptr[si],0
mov ax,0db00h
int 2fh
cmp al,0ffh
jne envtestend
cmp bx,5450h
jne envtestend
mov ax,1
int 79h
jne envtestend
mov word ptr[si],1
mov ax,11h
int 79h
jne envtestend
mov word ptr[si],3
mov ax,0ff00h
mov bx,0a03h
push es
push si
push bp
int 10h
pop bp
pop si
pop es
cmp al,0ffh
je envtestend
mov word ptr[si],7
envtestend:
mov sp,bp
pop bp
retf 2

getcharbitmap:
push bp
mov bp,sp
push ds
push es
lds si,[bp+6]
les di,[bp+10]
int 7eh
pop es
pop ds
mov sp,bp
pop bp
retf 8

;Params: color,x,y,w,h,si,ds
drawbitmap:
push bp
mov bp,sp
push ds
lds si,[bp+16]
mov dx,[bp+10]
mov ax,[bp+6]

yloop:
cmp word ptr[bp+14],0
je drawfinish
mov cx,[bp+8]
mov bl,80h
mov bh,[si]
mov di,[bp+12]

xloop:
cmp di,0
je xloopend
mov ah,bh
and ah,bl
jz skipdraw
mov ah,0ch
int 10h
skipdraw:
cmp bl,1
jne keepcurbytex
inc si
mov bh,[si]
keepcurbytex:
ror bl,1
inc cx
dec di
jmp xloop

xloopend:
cmp bl,80h
je keepcurbyte
inc si
keepcurbyte:
inc dx
dec word ptr[bp+14]
jmp yloop

drawfinish:
pop ds
mov sp,bp
pop bp
retf 14

codeend:
db 1ah

code ends
end start

