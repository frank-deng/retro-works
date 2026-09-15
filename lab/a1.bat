@echo off
del *.obj
del sudoku.com
tasm sudoku.asm, sudoku.obj
tlink /t sudoku.obj, sudoku.com
sudoku.com

