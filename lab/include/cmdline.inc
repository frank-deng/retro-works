IFNDEF MACRO_CMDLINE_INC
MACRO_CMDLINE_INC=1

include common.inc
extrn cmdparse:cPType

cmdinit MACRO
xor ch,ch
mov cl,es:[80h]
mov di,81h
ENDM

ENDIF

