@echo off
del *.obj
rem tasm uitoa.asm, uitoa.obj
rem tasm itoa.asm, itoa.obj
rem tlink /t @fntchk.lnk
TASM 24STAT
TLINK /t /x 24STAT
REN 24STAT.COM 24STAT.BIN

