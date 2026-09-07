.8086
.model tiny
BUFLEN EQU 10
TestCase STRUC
  LEN DW ?
  STR DB BUFLEN DUP(?)
  VAL DW ?
TestCase ENDS
include common.inc
extrn uitoa:cPType
extrn itoa:cPType
extrn atoui:cPType
extrn atoi:cPType
.code
org 100h
start:
lea di,[buf]
mov si,di
mov dx,di

;Enumerate 0x0-0xffff
xor bx,bx
test_nums_cycle:
mov ax,bx
call uitoa
call atoui
jc test_failed
cmp ax,bx
jne test_failed
call itoa
call atoi
jc test_failed
cmp ax,bx
jne test_failed
inc bx
jnz test_nums_cycle

;Test u16
lea bx,[test_u16_list]
test_u16_cycle:
mov ax,[bx].VAL
call uitoa
cmp cx,[bx].LEN
jne test_failed
call atoui
jc test_failed
cmp ax,[bx].VAL
jne test_failed
call cmp_str
jne test_failed
add bx,SIZE TestCase
cmp bx,offset test_u16_list_end
jb test_u16_cycle

;Test s16
lea bx,[test_s16_list]
test_s16_cycle:
mov ax,[bx].VAL
call itoa
cmp cx,[bx].LEN
jne test_failed
call atoi
jc test_failed
cmp ax,[bx].VAL
jne test_failed
call cmp_str
jne test_failed
add bx,SIZE TestCase
cmp bx,offset test_s16_list_end
jb test_s16_cycle

test_finish:
mov ah,09h
lea dx,[test_succeed_str]
int 21h
mov ax,4C00h
int 21h

test_failed:
mov cx,BUFLEN
lea dx,[buf]
mov bx,1
mov ah,40h
int 21h

cmp_str:
push si
push di
lea si,[bx].STR
cld
repe cmpsb
pop di
pop si
ret

mov ah,09h
lea dx,[test_failed_str]
int 21h
mov ax,4C01h
int 21h

test_failed_str db "Failed",0dh,0ah,"$"
test_succeed_str db "Succeed",0dh,0ah,"$"
test_u16_list:
TestCase<1,"0",0>
TestCase<1,"1",1>
TestCase<5,"32767",32767>
TestCase<5,"32768",32768>
TestCase<5,"65535",65535>
test_u16_list_end:
test_s16_list:
TestCase<1,"0",0>
TestCase<1,"1",1>
TestCase<5,"32767",32767>
TestCase<2,"-1",-1>
TestCase<6,"-32767",-32767>
TestCase<6,"-32768",-32768>
test_s16_list_end:
buf db BUFLEN DUP(?)

end start

