org 0h
;ans,guess,table_len,ds,si,es,di
push bp
mov bp,sp
sub sp,4
mov word[bp-2],0
mov ax,[bp+6]
mov bx,[bp+8]
call comp
cmp ax,0x40
je main_finish
push ds
mov dx,ax
mov si,[bp+10]
mov cx,[si]
mov ax,[bp+12]
mov ds,ax
mov si,[bp+14]
mov ax,[bp+16]
mov es,ax
mov di,[bp+18]
proc_loop:
mov ax,[si]
cmp ax,bx
je proc_next_num
call comp
cmp ax,dx
jne proc_next_num
mov ax,[si]
mov es:[di],ax
inc di
inc di
inc word[bp-2]
proc_next_num:
inc si
inc si
loop proc_loop
pop ds
mov ax,[bp-2]
mov si,[bp+10]
mov [si],ax
main_finish:
mov sp,bp
pop bp
retf 14

comp:
cmp ax,bx
jne comp_main
mov ax,0x40
ret
comp_main:
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
mov di,bp
sub di,20
mov cx,10
cld
rep stosw
mov cx,bx
and cx,0xf0f
call comp_writeres
mov cx,bx
shr cx,4
and cx,0xf0f
call comp_writeres
mov cx,dx
and cx,0xf0f
call comp_writeres
mov cx,dx
shr cx,4
and cx,0xf0f
call comp_writeres
mov cx,10
mov di,bp
dec di
dec di
comp_countb:
mov bx,ss:[di]
cmp bh,bl
jl comp_countb_min
add al,bl
jmp comp_countb_next
comp_countb_min:
add al,bh
comp_countb_next:
dec di
dec di
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
inc byte ss:[bp-20+di]
mov cl,ch
xor ch,ch
mov di,cx
shl di,1
inc byte ss:[bp-19+di]
ret
comp_a:
add al,0x10
ret
