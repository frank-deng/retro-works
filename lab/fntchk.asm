;How to compile:
;TASM FNTCHK
;TLINK /t /x FNTCHK
.8086
TARGET_FNAME EQU "FNTCHK.DOC"
BUF_SIZE EQU 512
QU_START EQU 0b0h
QU_END EQU 0f7h
WEI_START EQU 0a1h
WEI_END EQU 0feh
.model tiny
assume cs:code,ds:code,es:code,ss:code
code segment
org 100h
start:
mov ax,cs
mov ds,ax
mov es,ax

;Check if target file already exists
mov ah,4eh
xor cx,cx
lea dx,fname
int 21h
jnc target_file_exists

;Check whether UCDOS is running
mov ax,0db00h
int 2fh
cmp al,0ffh
jne run_ucdos_first
cmp bx,05450h
jne run_ucdos_first
mov ax,1
int 79h
jne run_ucdos_first

;Create target file
mov ah,3ch
xor cx,cx
lea dx,fname
int 21h
jc file_create_fail
mov [fhandle],ax

;Cycle fonts 0-8
xor ax,ax
mov cx,9
font_0_8:
call check_font
inc ax
loop font_0_8

;Font 9 may crash the system when rendering char after ECB3
;due to incomplete font file

;Cycle fonts 10-14
mov ax,10
mov cx,5
font_10_14:
call check_font
inc ax
loop font_10_14

;Cycle fonts 20-33
mov ax,20
mov cx,14
font_20_33:
call check_font
inc ax
loop font_20_33

jmp doexit

run_ucdos_first:
mov ah,09h
lea dx,run_ucdos_first_str
int 21h
mov ax,04c00h
int 21h

target_file_exists:
mov ah,09h
lea dx,target_file_exists_str
int 21h
mov ax,04c00h
int 21h

file_create_fail:
mov ah,09h
lea dx,file_create_fail_str
int 21h
mov ax,04c00h
int 21h

doexit:
mov bx,[fhandle]
cmp bx,0ffffh
je skip_close_file
mov ah,3eh
int 21h
skip_close_file:
mov ax,04c00h
int 21h

write_newline:
push ax
push bx
push cx
push dx
mov ah,40h
mov bx,word ptr[fhandle]
mov cx,2
lea dx,newline
int 21h
pop dx
pop cx
pop bx
pop ax
ret

write_num:
push bp
mov bp,sp
sub sp,4
push ax
push bx
push cx
push dx
mov byte ptr[bp-2],' '
aam
xchg ah,al
or ax,03030h
mov word ptr[bp-4],ax
mov ah,40h
mov bx,word ptr[fhandle]
mov cx,3
lea dx,word ptr[bp-4]
int 21h
pop dx
pop cx
pop bx
pop ax
mov sp,bp
pop bp
ret

check_font:
push bp
mov bp,sp
sub sp,8
push ax
push bx
push cx
push dx
call write_num
mov [bp-2],ax

call write_newline
pop dx
pop cx
pop bx
pop ax
mov sp,bp
pop bp
ret

target_file_exists_str db TARGET_FNAME," exists, please check.",0dh,0ah,"$"
run_ucdos_first_str db "Please run UCDOS and RDFNT first.",0dh,0ah,"$"
file_create_fail_str db "Failed to create ",TARGET_FNAME,0dh,0ah,"$"
fname db TARGET_FNAME,0,0
newline db 0dh,0ah
ALIGN 2
fhandle dw 0ffffh
buffer:

code ends
end start

