@echo off
tasm s16toa.asm, s16toa.obj
tasm 1.asm, 1.obj
tlink /t @1.lnk
