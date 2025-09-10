;How to compile
;tasm gstat.asm
;tlink /t /x gstat.obj
;bsave.exe gstat.com gstat.bin
code segment
org 100h
assume cs:code
start:
dw envtest-start
dw getcharbitmap-start

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

code ends
end start

