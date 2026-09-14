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
cnum.com 01>>cnum.txt
cnum.com 010>>cnum.txt
cnum.com 013>>cnum.txt
cnum.com 020>>cnum.txt
cnum.com 024>>cnum.txt
cnum.com 0100>>cnum.txt
cnum.com 0102>>cnum.txt
cnum.com 0192>>cnum.txt
cnum.com 0190>>cnum.txt
cnum.com 01000>>cnum.txt
cnum.com 01001>>cnum.txt
cnum.com 01020>>cnum.txt
cnum.com 01024>>cnum.txt
cnum.com 01200>>cnum.txt
cnum.com 01209>>cnum.txt
cnum.com 01249>>cnum.txt
cnum.com 010000>>cnum.txt
cnum.com 010002>>cnum.txt
cnum.com 011002>>cnum.txt
cnum.com 0100000>>cnum.txt
cnum.com 01000000>>cnum.txt
cnum.com 01040000>>cnum.txt
cnum.com 013040009>>cnum.txt
cnum.com 12345678912345678>>cnum.txt
cnum.com 1234567812345678>>cnum.txt


