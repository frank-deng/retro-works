10 DEFINT A-Z: DIM IMG(4096): SCREEN 2: CLS
20 T$ = "枫桥夜泊": F$ = "/f 0,3 /s 24,24 /c 4": X = 8: Y = 0: GOSUB 200
30 T$ = "张继": F$ = "/f 0,0 /s 12,12 /c 12": X = 80: Y = 28: GOSUB 200
40 T$ = "月落乌啼霜满天，": F$ = "": X = 0: Y = 55: GOSUB 200
50 T$ = "江枫渔火对愁眠。": F$ = "": X = 0: Y = 78: GOSUB 200
60 T$ = "姑苏城外寒山寺，": F$ = "": X = 0: Y = 101: GOSUB 200
70 T$ = "夜半钟声到客船。": F$ = "": X = 0: Y = 124: GOSUB 200
80 GET (0, 0)-(238, 139), IMG
90 DEF SEG = VARSEG(IMG(0)): BSAVE "POEM_T.PIC", VARPTR(IMG(0)), 4480: DEF SEG
100 CLS : PUT (0, 0), IMG
180 WHILE INPUT$(1) = "": WEND
190 SCREEN 0: END
200 SHELL "TEXT2BMP.EXE /O TEMP.BMP " + F$ + " " + T$
210 SHELL "BMP2CGA.EXE /COLOR3 TEMP.BMP TEMP.PIC"
220 DEF SEG = VARSEG(IMG(0)): BLOAD "TEMP.PIC", VARPTR(IMG(0)): DEF SEG
230 PUT (X, Y), IMG, PSET: RETURN

