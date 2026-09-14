@echo off
del *.obj
del cnum.com
del cnum.txt
tasm cnum.asm, cnum.obj
tlink /t cnum.obj, cnum.com
cnum.com 01234567890>cnum.txt
cnum.com 01200000000>>cnum.txt
cnum.com 01200010000>>cnum.txt
cnum.com 01200002000>>cnum.txt
cnum.com 00>>cnum.txt

