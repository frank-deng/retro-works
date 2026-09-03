@echo off
del *.obj
tasm uitoa.asm, uitoa.obj
tasm itoa.asm, itoa.obj
tasm atoui.asm, atoui.obj
tasm atoi.asm, atoi.obj
rem tasm test.asm, test.obj
tasm 1.asm, 1.obj
tlink /t @1.lnk

