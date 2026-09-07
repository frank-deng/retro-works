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

call test_u16
jc test_failed
call test_s16
jc test_failed

;Test u16 abnormal
lea bx,[test_u16_abnormal]
test_u16_abnormal_cycle:
mov cx,[bx].LEN
lea si,[bx].STR
call atoui
jnc test_failed
call atoi
jnc test_failed
add bx,SIZE TestCase
cmp bx,offset test_u16_abnormal_end
jb test_u16_abnormal_cycle

;Test s16 abnormal
lea bx,[test_s16_abnormal]
test_s16_abnormal_cycle:
mov cx,[bx].LEN
lea si,[bx].STR
call atoi
jnc test_failed
add bx,SIZE TestCase
cmp bx,offset test_s16_abnormal_end
jb test_s16_abnormal_cycle

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

test_s16:
lea bx,[test_s16_list]
test_s16_cycle:
mov ax,[bx].VAL
call itoa
call check_res
jc test_s16_failed
call atoi
jc test_s16_failed
call check_res
jc test_s16_failed
add bx,SIZE TestCase
cmp bx,offset test_s16_list_end
jb test_s16_cycle
clc
ret
test_s16_failed:
stc
ret

test_u16:
lea bx,[test_u16_list]
test_u16_cycle:
mov ax,[bx].VAL
call uitoa
call check_res
jc test_u16_failed
call atoui
jc test_u16_failed
call check_res
jc test_u16_failed
add bx,SIZE TestCase
cmp bx,offset test_u16_list_end
jb test_u16_cycle
clc
ret
test_u16_failed:
stc
ret

check_res:
push cx
push si
push di
cmp ax,[bx].VAL
jne check_res_failed
cmp cx,[bx].LEN
jne check_res_failed
lea si,[bx].STR
cld
repe cmpsb
jne check_res_failed
check_res_finish:
pop di
pop si
pop cx
ret
check_res_failed:
stc
jmp check_res_finish

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
test_u16_abnormal:
TestCase<3,"1aa",0>
TestCase<6,"123456",0>
TestCase<6,"100000",0>
TestCase<5,"65536",0>
test_u16_abnormal_end:
test_s16_abnormal:
TestCase<5,"32768",0>
TestCase<5,"65535",0>
TestCase<6,"-32769",0>
TestCase<6,"-65535",0>
test_s16_abnormal_end:
buf db BUFLEN DUP(?)

end start

