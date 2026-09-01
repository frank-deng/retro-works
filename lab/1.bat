@echo off
del *.obj
tasm uitoa.asm, uitoa.obj
tasm itoa.asm, itoa.obj
tasm 1.asm, 1.obj
tlink /t @1.lnk
