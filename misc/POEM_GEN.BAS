10 DEFINT A-Z: DIM IMG(4096): SCREEN 2: CLS
20 T$ = "∑„«≈“π≤¥": F$ = "/f 0,3 /s 24,24 /c 4": X = 8: Y = 0: GOSUB 200
30 T$ = "’≈ºÃ": F$ = "/f 0,0 /s 12,12 /c 12": X = 80: Y = 28: GOSUB 200
40 T$ = "‘¬¬‰Œ⁄Ã‰À™¬˙ÃÏ£¨": F$ = "": X = 0: Y = 55: GOSUB 200
50 T$ = "Ω≠∑„”Êª∂‘≥Ó√ﬂ°£": F$ = "": X = 0: Y = 78: GOSUB 200
60 T$ = "π√À’≥«Õ‚∫Æ…ΩÀ¬£¨": F$ = "": X = 0: Y = 101: GOSUB 200
70 T$ = "“π∞Î÷”…˘µΩøÕ¥¨°£": F$ = "": X = 0: Y = 124: GOSUB 200
80 GET (0, 0)-(238, 139), IMG: CLS: PUT (42, 30), IMG, PSET
90 SHELL "BMP2CGA.EXE POEM.BMP TEMP.PIC"
100 DEF SEG = VARSEG(IMG(0)): BLOAD "TEMP.PIC", VARPTR(IMG(0)): DEF SEG
110 PUT (320, 30), IMG, PSET
120 DEF SEG = &HB800: BSAVE "POEM.PIC", 0, 16384: DEF SEG
130 WHILE INPUT$(1) = "": WEND: SCREEN 0
140 KILL "TEMP.BMP": KILL "TEMP.PIC": END
200 SHELL "TEXT2BMP.EXE /O TEMP.BMP " + F$ + " " + T$
210 SHELL "BMP2CGA.EXE /COLOR3 TEMP.BMP TEMP.PIC"
220 DEF SEG = VARSEG(IMG(0)): BLOAD "TEMP.PIC", VARPTR(IMG(0)): DEF SEG
230 PUT (X, Y), IMG, PSET: RETURN