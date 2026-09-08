IFNDEF MACRO_COMMON_INC
MACRO_COMMON_INC=1

; memset —— 用 rep stosw 按字填充内存 (兼容 MASM/TASM/WASM)
;   参数: dstseg=目标段(装入 ES), off=目标偏移(装入 DI), val=填充值(装入 AX),
;         count=填充字数(装入 CX, 字节数为 count*2)
;   无返回值; 不保护寄存器(破坏 CX, 并改写 ES/DI/AX)
memset MACRO dstseg, off, val, count
    mov ax, dstseg
    mov es, ax
    mov ax, val
    lea di, off
    mov cx, count
    cld
    rep stosw
ENDM

; cPType —— 按当前内存模型选择代码指针距离(near/far)
;   near: tiny/small/compact     far: medium/large/huge
;   注意: 本文件必须在 .model 之后 include, 否则 @CodeSize 尚未定义
ifdef @Model
    ife @CodeSize-2
        cPType  equ <far>
    else
        cPType  equ <near>
    endif
endif

ENDIF

