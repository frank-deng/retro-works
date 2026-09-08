@echo off
del *.obj
del 24solve.com
tasm /iinclude lib\uitoa.asm, uitoa.obj
tasm /iinclude lib\atoui.asm, atoui.obj
tasm /iinclude lib\cmdline.asm, cmdline.obj
tasm /iinclude 24solve.asm, 24solve.obj
tlink /t 24solve.obj cmdline.obj uitoa.obj atoui.obj, 24solve.com

