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
codeend:
db 1ah
code ends
end start

