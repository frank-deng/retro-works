@echo off
del *.obj
del 2.com
tasm 2.asm, 2.obj
tlink /t 2.obj, 2.com
2.com 1 2 3 4 12

