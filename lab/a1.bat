@echo off
del *.obj
del sudoku.com
tasm sudoku.asm, sudoku.obj
tlink /t sudoku.obj, sudoku.com
sudoku.com ..\sudoku\sudoku.txt
sudoku.com ..\sudoku\sudoku3.txt
sudoku.com ..\sudoku\sudokum1.txt
sudoku.com ..\sudoku\sudokum1.txt ..\sudoku\sudkumap.txt


