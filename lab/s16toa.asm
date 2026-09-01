; s16toa.asm -- segment-agnostic 16-bit signed integer to ASCII
;
; Converts the 16-bit signed integer in AX to a decimal ASCII string
; into the buffer pointed to by ES:DI. The routine is model-independent:
; it never reads DS and never assumes the content of any segment
; register, so it assembles and runs correctly under tiny / small /
; medium / compact / large / huge memory models alike.
;
; The ES:DI buffer convention mirrors the int 21h / int 10h practice of
; passing a buffer address through ES plus a register offset.
;
; Entry:
;   AX    = signed 16-bit value (-32768 .. 32767)
;   ES:DI = output buffer (needs up to 6 bytes: sign + 5 digits)
; Exit:
;   CX    = number of characters written (sign included)
;   ES:DI = points one byte past the last written character
;           (no terminating NUL / '$' is written -- caller's job)
; Clobbers: AX, BX, CX, DX
; Preserves: SI, DI, and all other registers
;
; Assemble with any model, e.g.:
;   tasm s16toa.asm        (uses the .model below, or override with
;                           -mt / -ms / -mm / -mc / -ml / -mh)

    .8086
    .model small            ; tiny/small/medium/compact/large/huge all fine

    .code

    public s16toa

s16toa proc
    push ax
    push bx
    push dx
    push si
    push di

    mov  si, di                ; SI = buffer start, used for the length count

    or   ax, ax
    jns  positive              ; AX >= 0
    neg  ax                    ; AX = |AX|
    mov  byte ptr es:[di], '-' ; emit sign
    inc  di

positive:
    cmp  ax, 10
    jl   emit_units            ; 0..9
    cmp  ax, 100
    jl   emit_tens             ; 10..99
    cmp  ax, 1000
    jl   emit_hundreds         ; 100..999
    cmp  ax, 10000
    jl   emit_thousands        ; 1000..9999

    ; 10000..32767: ten-thousands digit
    xor  dx, dx                ; AX is non-negative here, so clear DX
    mov  bx, 10000
    div  bx
    add  al, '0'
    mov  byte ptr es:[di], al
    inc  di
    mov  ax, dx

emit_thousands:                ; 1000..9999
    xor  dx, dx
    mov  bx, 1000
    div  bx
    add  al, '0'
    mov  byte ptr es:[di], al
    inc  di
    mov  ax, dx

emit_hundreds:                 ; 100..999
    xor  dx, dx
    mov  bx, 100
    div  bx
    add  al, '0'
    mov  byte ptr es:[di], al
    inc  di
    mov  ax, dx

emit_tens:                     ; 10..99
    aam                        ; AH = AL/10 (tens), AL = AL%10 (units)
    add  ah, '0'
    mov  byte ptr es:[di], ah  ; tens digit
    inc  di

emit_units:                    ; 0..9
    add  al, '0'
    mov  byte ptr es:[di], al  ; units digit
    inc  di

    mov  cx, di
    sub  cx, si                ; CX = characters written

    pop  di
    pop  si
    pop  dx
    pop  bx
    pop  ax
    ret
s16toa endp

    end
