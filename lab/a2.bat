@echo off
del *.obj
del 24solve.com
tasm 24solve.asm, 24solve.obj
tlink /t 24solve.obj, 24solve.com
24solve.com 5 5 5 1
24solve.com 7 5 3 8

