@echo off
del *.obj
tasm uitoa.asm, uitoa.obj
tasm itoa.asm, itoa.obj
tasm atoui.asm, atoui.obj
tasm atoi.asm, atoi.obj
tasm test.asm, test.obj
rem tasm 1.asm, 1.obj
rem tlink /t @1.lnk
tlink /t @test.lnk

