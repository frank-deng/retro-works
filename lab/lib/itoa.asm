; itoa.asm -- segment-agnostic 16-bit signed integer to ASCII
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
;   tasm itoa.asm        (uses the .model below, or override with
;                           -mt / -ms / -mm / -mc / -ml / -mh)

    .8086
    .model small            ; tiny/small/medium/compact/large/huge all fine
    include common.inc
    extrn uitoa:cPType

    .code
    public itoa

itoa proc cPType
    push ax
    push si
    push di

    mov  si, di                ; SI = buffer start, used for the length count

    or   ax, ax
    jns  positive              ; AX >= 0
    neg  ax                    ; AX = |AX|
    mov  byte ptr es:[di], '-' ; emit sign
    inc  di
positive:
    call uitoa
    cmp si,di
    je finish
    inc cx
finish:
    pop di
    pop si
    pop ax
    ret
itoa endp

    end
