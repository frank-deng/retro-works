@echo off
del *.obj
del 1.com
tasm /iinclude lib\hextable.asm, hextable.obj
tasm /iinclude lib\uitox.asm, uitox.obj
tasm /iinclude lib\cmdline.asm, cmdline.obj
tasm /iinclude 1.asm, 1.obj
tlink /t @1.lnk
1.com         12345       hahaha
1.com a b
1.com
1.com        

