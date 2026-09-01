IFNDEF MACRO_COMMON_INC
MACRO_COMMON_INC=1

; memset —— 用 rep stosw 按字填充内存 (兼容 MASM/TASM/WASM)
;   参数: seg=目标段(装入 ES), off=目标偏移(装入 DI), val=填充值(装入 AX),
;         count=填充字数(装入 CX, 字节数为 count*2)
;   无返回值; 不保护寄存器(破坏 CX, 并改写 ES/DI/AX)
memset MACRO seg, off, val, count
    mov ax, seg
    mov es, ax
    mov ax, val
    mov di, off
    mov cx, count
    cld
    rep stosw
ENDM

ENDIF

