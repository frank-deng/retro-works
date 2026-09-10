.8086
.model tiny
BUFLEN EQU 10
TestCase STRUC
  LEN DW ?
  NSTR DB BUFLEN DUP(?)
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
not ax
call atoui
jnc test_nums_atoui_ok
jmp test_failed
test_nums_atoui_ok:
cmp ax,bx
je test_nums_u16_equal
jmp test_failed
test_nums_u16_equal:
call itoa
not ax
call atoi
jnc test_nums_atoi_ok
jmp test_failed
test_nums_atoi_ok:
cmp ax,bx
je test_nums_s16_equal
jmp test_failed
test_nums_s16_equal:
inc bx
jnz test_nums_cycle

;Test U16
;call test_u16
;jc test_failed
lea bx,[test_u16_list]
test_u16_cycle:
clc
mov ax,[bx].VAL
call uitoa
call check_res
jnc test_u16_uitoa_ok
jmp test_failed
test_u16_uitoa_ok:
call atoui
call check_res
jnc test_u16_atoui_ok
jmp test_failed
test_u16_atoui_ok:
add bx,SIZE TestCase
cmp bx,offset test_u16_list_end
jb test_u16_cycle

;Test S16
lea bx,[test_s16_list]
test_s16_cycle:
clc
mov ax,[bx].VAL
call itoa
call check_res
jnc test_s16_itoa_ok
jmp test_failed
test_s16_itoa_ok:
call atoi
call check_res
jnc test_s16_atoi_ok
jmp test_failed
test_s16_atoi_ok:
add bx,SIZE TestCase
cmp bx,offset test_s16_list_end
jb test_s16_cycle

;Test u16 abnormal
lea bx,[test_u16_abnormal]
test_u16_abnormal_cycle:
clc
mov cx,[bx].LEN
lea si,[bx].NSTR
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
clc
mov cx,[bx].LEN
lea si,[bx].NSTR
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
mov ah,09h
lea dx,[test_failed_str]
int 21h
mov ax,4C01h
int 21h

check_res:
push cx
push si
push di
jc check_res_failed
cmp ax,[bx].VAL
jne check_res_failed
cmp cx,[bx].LEN
jne check_res_failed
lea si,[bx].NSTR
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

