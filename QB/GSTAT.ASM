;How to compile:
;TASM GSTAT
;TLINK /t /x GSTAT
;REN GSTAT.COM GSTAT.BIN
;Params: ans,guess,table_len,si,ds,di,es
code segment
org 100h
assume cs:code
start:
db 0fdh
dw 0
dw 100h
dw endcode-startcode
startcode:
push bp
mov bp,sp
sub sp,2
push ds
push es
mov word ptr[bp-2],0
mov ax,[bp+6]
mov bx,[bp+8]
call comp
mov dx,ax
mov si,[bp+10]
mov cx,[si]
lds si,[bp+12]
les di,[bp+16]
proc_loop:
mov ax,[si]
cmp ax,bx
je proc_next_num
call comp
cmp ax,dx
jne proc_next_num
mov ax,[si]
mov es:[di],ax
add di,2
inc word ptr[bp-2]
proc_next_num:
add si,2
loop proc_loop
pop es
pop ds
mov ax,[bp-2]
mov si,[bp+10]
mov [si],ax
mov sp,bp
pop bp
retf 14

comp:
push bp
mov bp,sp
sub sp,20
push bx
push cx
push dx
push es
push di
xchg al,bh
mov dx,ax
mov ax,ss
mov es,ax
xor ax,ax
lea di,[bp-20]
mov cx,10
cld
rep stosw
mov cx,bx
and cx,0f0fh
call comp_writeres
mov cx,bx
shr cx,4
and cx,0f0fh
call comp_writeres
mov cx,dx
and cx,0f0fh
call comp_writeres
mov cx,dx
shr cx,4
and cx,0f0fh
call comp_writeres
mov cx,10
lea di,[bp-2]
comp_countb:
mov bx,ss:[di]
cmp bh,bl
jl comp_countb_min
add al,bl
jmp comp_countb_next
comp_countb_min:
add al,bh
comp_countb_next:
sub di,2
loop comp_countb
comp_finish:
pop di
pop es
pop dx
pop cx
pop bx
mov sp,bp
pop bp
ret
comp_writeres:
cmp ch,cl
je comp_a
mov di,cx
xor ch,ch
xchg cx,di
shl di,1
inc byte ptr ss:[bp-20+di]
mov cl,ch
xor ch,ch
mov di,cx
shl di,1
inc byte ptr ss:[bp-19+di]
ret
comp_a:
add al,10h
ret
endcode:
db 1ah
code ends
end start
