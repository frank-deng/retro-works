section .text
global main
  org 100h
main:
  mov ax,cs
  mov ds,ax
  mov ah,9
  mov dx,msge
  int 21h
  mov ah, 4ch
  int 21h
msge:
  db 'Hello World!',0dh,0ah,'$'
