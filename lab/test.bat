@echo off
del *.obj
del test.com
tasm uitoa.asm, uitoa.obj
tasm itoa.asm, itoa.obj
tasm atoui.asm, atoui.obj
tasm atoi.asm, atoi.obj
tasm test.asm, test.obj
tlink /t @test.lnk
test.com

