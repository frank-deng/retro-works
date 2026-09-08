@echo off
del *.obj
del test.com
tasm /iinclude lib\uitoa.asm, uitoa.obj
tasm /iinclude lib\itoa.asm, itoa.obj
tasm /iinclude lib\atoui.asm, atoui.obj
tasm /iinclude lib\atoi.asm, atoi.obj
tasm /iinclude test.asm, test.obj
tlink /t @test.lnk
test.com

