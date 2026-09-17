;==============================================================================
; CNUM.ASM  --  Convert a decimal number to Chinese financial uppercase
;               numerals (零壹贰叁肆伍陆柒捌玖拾佰仟万亿).
;
;   Build : tasm cnum.asm, cnum.obj
;           tlink /t cnum.obj, cnum.com
;   Usage : cnum 123456789  ->  壹亿贰仟叁佰肆拾伍万陆仟柒佰捌拾玖
;
;   Note  : num_str is stored as raw GBK bytes below, so the source file
;           encoding (UTF-8 / GBK) does not matter.
;==============================================================================

    .8086

;------------------------- constants --------------------------------------
MAX_LEN     EQU 16      ; max chars in the command-line argument
MAX_DIGITS  EQU 16      ; max significant digits
HALF_DIGITS EQU 8       ; digits per 1e8 (亿) segment

STD_OUT     EQU 1       ; DOS handle: stdout
DOS_WRITE   EQU 40h     ; int 21h: write file
DOS_EXIT    EQU 4Ch     ; int 21h: terminate

UNIT_SHI    EQU 10      ; index of 拾 in num_str
UNIT_WAN    EQU 13      ; index of 万
UNIT_YI     EQU 14      ; index of 亿

;------------------------- code -------------------------------------------
    .model tiny
    .code
    org 100h

start:
    ;--- fetch first command-line argument from PSP ---
    xor  ch, ch              ; clear ch: cl will hold the tail length
    mov  cl, es:[80h]        ; cl = command tail length
    mov  di, 81h             ; command tail buffer
    call getcmditem          ; -> si = token start, di = token end
    cmp  si, di
    je   fail                ; no argument

    ;--- length check ---
    mov  cx, di
    sub  cx, si              ; cx = token length
    cmp  cx, MAX_LEN
    ja   fail                ; too long

    ;--- validate digits, strip leading zeros, store values ---
    xor  bx, bx              ; bx = significant digit count
    lea  di, [src_buf]
loop_str:
    lodsb                    ; al = next char
    sub  al, '0'             ; -> 0..9
    cmp  al, 9
    ja   fail                ; not a digit
    test al, al
    jnz  store               ; non-zero -> keep
    test bx, bx
    jz   skip                ; still in leading zeros -> drop
store:
    inc  bx
    stosb
skip:
    loop loop_str

    ;--- significant digit count check ---
    mov  cx, bx
    cmp  cx, MAX_DIGITS
    ja   fail
    jcxz zero                ; all zeros -> "零"

    ;--- split into 亿 segment + 万/个 segment ---
    lea  si, [src_buf]
    cmp  cx, HALF_DIGITS
    jbe  low_seg             ; <= 8 digits, no 亿 segment
    sub  cx, HALF_DIGITS     ; cx = 亿 segment length
    call proc_1e8            ; emit 亿 segment
    mov  ax, UNIT_YI
    call disp_val            ; "亿"
    add  si, cx              ; si -> low segment
    mov  cx, HALF_DIGITS
low_seg:
    call proc_1e8            ; emit 万/个 segment
    jmp  exit_ok

zero:
    xor  ax, ax
    call disp_val            ; "零"

exit_ok:
    lea  dx, [newline_str]
    mov  ah, DOS_WRITE
    mov  bx, STD_OUT
    mov  cx, 2
    int  21h
    mov  ah, DOS_EXIT
    mov  al, 0
    int  21h

fail:
    mov  ah, DOS_EXIT
    mov  al, 1               ; exit code 1
    int  21h

;--------------------------------------------------------------------------
; getcmditem - extract one whitespace-delimited token at es:di.
;   in : cx = remaining chars, es:di = start
;   out: si = token start, di = token end (si == di when empty)
;   modifies: ax, cx, si, di
;--------------------------------------------------------------------------
getcmditem:
    push ax
    jcxz getcmditem_empty
    mov  al, ' '
    cld
    repe scasb               ; skip leading spaces
    je   getcmditem_empty    ; nothing but spaces
    dec  di                  ; di -> first non-space
    inc  cx
    mov  si, di              ; si = token start
    repne scasb              ; find next space
    jne  getcmditem_end      ; hit end of tail
    dec  di                  ; di -> the space
    inc  cx
getcmditem_end:
    pop  ax
    ret
getcmditem_empty:
    mov  si, di
    jmp  getcmditem_end

;--------------------------------------------------------------------------
; disp_val - write one 2-byte GBK character from num_str.
;   in : al = character index
;   modifies: nothing (all regs preserved)
;--------------------------------------------------------------------------
disp_val:
    push ax
    push bx
    push cx
    push dx
    mov  dl, al
    xor  dh, dh
    shl  dx, 1               ; index * 2 = byte offset
    add  dx, offset num_str
    mov  ah, DOS_WRITE
    mov  bx, STD_OUT
    mov  cx, 2
    int  21h
    pop  dx
    pop  cx
    pop  bx
    pop  ax
    ret

;--------------------------------------------------------------------------
; proc_1e8 - emit a segment of up to 8 digits ("X 万 X" inside a 亿 segment).
;   in : si = segment start (digit bytes), cx = segment length (1..8)
;   out: si, cx unchanged
;--------------------------------------------------------------------------
proc_1e8:
    push ax
    push bx
    push cx
    push dx
    push si
    push di
    mov  di, si
    xor  al, al
    cld
    repe scasb               ; skip leading zero digits
    je   no_disp_1e8         ; all zero -> emit nothing
    inc  cx                  ; cx = remaining count incl. first non-zero
    dec  di                  ; di -> first non-zero
    cmp  byte ptr [si], 0
    jne  no_leading_zero_1e8
    xor  ax, ax
    call disp_val            ; leading zero -> "零"
no_leading_zero_1e8:
    mov  si, di              ; si -> first non-zero
    cmp  cx, 4
    jbe  low_4               ; <= 4 digits, no 万
    sub  cx, 4               ; cx = 万 sub-segment length
    call proc_1e4            ; emit 万 sub-segment
    mov  ax, UNIT_WAN
    call disp_val            ; "万"
    add  si, cx              ; si -> 个 sub-segment
    mov  cx, 4
low_4:
    call proc_1e4            ; emit 个 sub-segment
no_disp_1e8:
    pop  di
    pop  si
    pop  dx
    pop  cx
    pop  bx
    pop  ax
    ret

;--------------------------------------------------------------------------
; proc_1e4 - emit a segment of up to 4 digits (仟佰拾个).
;   in : si = segment start, cx = segment length (1..4)
;   out: si, cx unchanged
;--------------------------------------------------------------------------
proc_1e4:
    push ax
    push bx
    push cx
    push si
    push di
    mov  ah, 0FFh            ; ah = previous digit (0FFh = none yet)
proc_digits_1e4:
    lodsb
    mov  bh, al
    test al, al
    jz   skip_digit_1e4      ; zero digit -> skip
    test ah, ah
    jnz  no_prefix_zero_1e4  ; previous non-zero -> no "零" prefix
    xor  al, al
    call disp_val            ; "零"
    mov  al, bh
no_prefix_zero_1e4:
    call disp_val            ; the digit itself
    cmp  cx, 1
    jz   skip_digit_1e4      ; units digit -> no suffix
    mov  al, UNIT_SHI - 2
    add  al, cl              ; cl = 2/3/4 -> 拾/佰/仟
    call disp_val
skip_digit_1e4:
    mov  ah, bh              ; remember this digit
    loop proc_digits_1e4
    pop  di
    pop  si
    pop  cx
    pop  bx
    pop  ax
    ret

;------------------------- data (raw GBK bytes) ---------------------------
; num_str = 零壹贰叁肆伍陆柒捌玖拾佰仟万亿
num_str     db 0C1h,0E3h, 0D2h,0BCh, 0B7h,0A1h, 0C8h,0FEh, 0CBh,0C1h
            db 0CEh,0E9h, 0C2h,0BDh, 0C6h,0E2h, 0B0h,0C6h, 0BEh,0C1h
            db 0CAh,0B0h, 0B0h,0DBh, 0C7h,0AAh, 0CDh,0F2h, 0D2h,0DAh
newline_str db 0Dh, 0Ah
src_buf     db MAX_DIGITS dup(?)   ; digit buffer (was previously unallocated)

    end start

