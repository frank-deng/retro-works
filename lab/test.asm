.8086
.model tiny
BUFLEN EQU 10
TestCase STRUC
  LEN DW ?
  NSTR DB BUFLEN DUP(?)
  VAL DW ?
TestCase ENDS
TestCaseCTZ STRUC
  NUM DW ?
  RES DW ?
TestCaseCTZ ENDS
include common.inc
extrn uitoa:cPType
extrn itoa:cPType
extrn atoui:cPType
extrn atoi:cPType
extrn ctz:cPType
.code
org 100h
start:
mov ax,cs
mov ds,ax
mov es,ax

;Enumerate 0x0-0xffff
lea di,[buf]
mov si,di
xor bx,bx
test_nums_cycle:
mov ax,bx
mov di,si
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
mov di,si
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
lea bx,[test_u16_list]
test_u16_cycle:
memset ES [buf] 0 BUFLEN/2
lea di,[buf]
mov si,di
clc
mov ax,[bx].VAL
call uitoa
call check_res
jnc test_u16_uitoa_ok
jmp test_failed
test_u16_uitoa_ok:
not ax
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
memset ES [buf] 0 BUFLEN/2
lea di,[buf]
mov si,di
clc
mov ax,[bx].VAL
call itoa
call check_res
jnc test_s16_itoa_ok
jmp test_failed
test_s16_itoa_ok:
not ax
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
jc test_u16_abnormal_atoui_ok
jmp test_failed
test_u16_abnormal_atoui_ok:
call atoi
jc test_u16_abnormal_atoi_ok
jmp test_failed
test_u16_abnormal_atoi_ok:
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
jc test_s16_abnormal_atoi_ok
jmp test_failed
test_s16_abnormal_atoi_ok:
add bx,SIZE TestCase
cmp bx,offset test_s16_abnormal_end
jb test_s16_abnormal_cycle

;Test CTZ
lea bx,[test_ctz]
test_ctz_cycle:
mov ax,[bx].NUM
call ctz
jnc test_ctz_call_ok
jmp test_failed
test_ctz_call_ok:
cmp ax,[bx].RES
je test_ctz_res_ok
jmp test_failed
test_ctz_res_ok:
add bx,SIZE TestCaseCTZ
cmp bx,offset test_ctz_end
jb test_ctz_cycle
xor ax,ax
call ctz
jc test_ctx_zero_ok
jmp test_failed
test_ctx_zero_ok:

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
lea di,[buf]
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

print_val:
push bp
mov bp,sp
sub sp,8
push ax
push bx
push cx
push dx
push di
push ds
push es
mov dx,ss
mov es,dx
mov ds,dx
lea dx,[bp-8]
mov di,dx
call uitoa
add di,cx
mov es:[di],0a0dh
mov ah,40h
mov bx,1
inc cx
inc cx
int 21h
pop es
pop ds
pop di
pop dx
pop cx
pop bx
pop ax
mov sp,bp
pop bp
ret

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
test_ctz:
TestCaseCTZ<1,0>
TestCaseCTZ<9,0>
TestCaseCTZ<2,1>
TestCaseCTZ<0ah,1>
TestCaseCTZ<4,2>
TestCaseCTZ<8,3>
TestCaseCTZ<080h,7>
TestCaseCTZ<0800h,11>
test_ctz_end:
buf db BUFLEN DUP(0)

end start

