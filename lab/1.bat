@echo off
del *.obj
del 1.com
tasm hextable.asm, hextable.obj
tasm uitox.asm, uitox.obj
tasm 1.asm, 1.obj
tlink /t @1.lnk
1.com

