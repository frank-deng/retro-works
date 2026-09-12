@echo off
del *.obj
del cnum.com
tasm cnum.asm, cnum.obj
tlink /t cnum.obj, cnum.com
cnum.com 01234567890
