DECLARE SUB TestTX ()
DECLARE FUNCTION n$ (n%)
DECLARE FUNCTION nd$ (A#)
DECLARE FUNCTION percent$ (A#)
DECLARE SUB TX (s AS STRING)
DECLARE SUB DrawText (x AS INTEGER, y AS INTEGER, text AS STRING)
DECLARE SUB DrawBar (x AS INTEGER, y AS INTEGER, w AS INTEGER, l AS SINGLE, pc AS DOUBLE, v as double)
DATA &H50,&H53,&H56,&HBE,&H00,&H00,&H2E,&HC7,&H04,&H00,&H00,&HB8,&H00,&HDB,&HCD,&H2F
DATA &H3C,&HFF,&H75,&H12,&H81,&HFB,&H50,&H54,&H75,&H0C,&HB8,&H11,&H00,&HCD,&H79,&H75
DATA &H05,&h2E,&HC7,&H04,&H01,&H00,&H5E,&H5B,&H58,&HCB

DEFINT A-Z: COMMON COL, BG, RADIUS
TestTX

' Prepare data
S# = 0: MAX# = 0: C = 0: TL = 0
COL = 15: BG = 0: RADIUS = 200
DIM LABEL$(2048),VALUE#(2048)

INPUT "请输入文件名：", F$
OPEN F$ FOR INPUT AS #2
WHILE NOT EOF(2)
  INPUT #2, T$, D#
  TL0 = LEN(T$)
  IF TL0 > TL THEN TL = TL0
  IF D# > MAX# THEN MAX# = D#
  S# = S# + D#: C = C + 1
  LABEL$(C)=T$:VALUE#(C)=D#
WEND
CLOSE #2

OPEN "LPT3" FOR OUTPUT AS #1
TX ("M10CU1,0KB1,0CL0CO" + n$(BG) + "B0,0,640,480")
TX ("{=0%1@12,12}")

Y = 0 : TL = TL * 6
FOR I = 1 TO C
  T$=LABEL$(I):D#=VALUE#(I)
  TX ("{(" + n$(COL) + "}")
  CALL DrawText(0, Y, T$)
  CALL DrawBar(TL + 2, Y, 639 - TL, D# / MAX#, D# / S#, D#)
  IF (I MOD 38)<>0 OR I=L THEN
    Y=Y+12
  ELSE
    TX ("{(" + n$(COL) + "}")
    CALL DrawText(0, 480-16, "请按任意键继续")
    WHILE INPUT$(1)="":WEND:Y=0
    TX ("CL0CO" + n$(BG) + "B0,400,640,480CO7")
  END IF
NEXT I

WHILE INPUT$(1) = "": WEND
IF C>27 THEN TX ("KB1,1M3CU1,1"):CLOSE:END

' Start drawing pie chart
TX ("CL0CO"+n$(BG)+"B0,460,640,480CO7")

K1#=0: K2#=VALUE#(1)
TX ("{(15@16,16}")
LH = 18: TOP = (480-C*LH)/2
FOR I=1 TO C
  T$=LABEL$(I):D#=VALUE#(I)
  IF I=C THEN
    COL = 1
    CALL DrawPie(430, 240, FIX(K1#/S#*360), 360, 1)
  ELSE
    COL = ((I-1) mod 13)+2
    CALL DrawPie(430, 240, FIX(K1#/S#*360), FIX(K2#/S#*360), COL)
    K1#=K1#+VALUE#(I):K2#=K2#+VALUE#(I+1)
  ENDIF
  TX ("CO"+n$(COL)+"B5,"+n$(I*LH+TOP)+","+n$(5+15)+","+n$(I*LH+TOP+15))
  CALL DrawText(5+16+6,I*LH+TOP,T$+"（"+percent$(D#/S#)+"）")
NEXT I

WHILE INPUT$(1) = "": WEND
TX ("KB1,1M3CU1,1")
CLOSE:END

SUB DrawPie(x as integer,y as integer, sangle as integer, angle as integer, col as integer)
  SHARED RADIUS
  IF sangle <> angle then
    TX("CO"+n$(col)+"E" + n$(x) + "," + n$(y)+","+n$(sangle)+","+n$(angle)+","+n$(RADIUS)+","+n$(RADIUS)+",2,"+n$(col))
  end if
END SUB

SUB DrawBar (x AS INTEGER, y AS INTEGER, w AS INTEGER, l AS SINGLE, pc AS DOUBLE, v as DOUBLE)
  SHARED COL, BG
  TX ("CO" + n$(COL) + "B" + n$(x) + "," + n$(y) + "," + n$(FIX(x + w * l)) + "," + n$(y + 10))
  SN$ = nd$(v)+"（"+percent$(pc)+"）"
  SNL = LEN(SN$) * 6 + 4
  IF l < .5 THEN
    TX ("{(" + n$(COL) + "}"): CALL DrawText(x + w * l + 4, y, SN$)
  ELSE
    TX ("{(" + n$(BG) + "}"): CALL DrawText(x + w * l - SNL, y, SN$)
  END IF
END SUB

SUB DrawText (x AS INTEGER, y AS INTEGER, text AS STRING)
  TX ("{-" + n$(x) + "|" + n$(y) + CHR$(0) + text + "}")
END SUB

FUNCTION n$ (A)
n$ = LTRIM$(RTRIM$(STR$(A)))
END FUNCTION

FUNCTION nd$ (A AS DOUBLE)
nd$ = LTRIM$(RTRIM$(STR$(A)))
END FUNCTION

FUNCTION percent$(A AS DOUBLE)
  p# = FIX(A * 100000 + 0.5) / 1000
  pn$ = nd$(p#):if p#<1 and p#>0 then pn$ = "0"+pn$
  percent$ = mid$(pn$, 1, len(str$(fix(p#)))+3) + "%"
END FUNCTION

SUB TestTX
DIM A%(50)
DEF SEG = VARSEG(A%(0))
RESTORE
FOR I% = 0 TO 41
    READ D%
    IF I% = 4 THEN
       D% = VARPTR(A%(49)) MOD 256
    ELSEIF I% = 5 THEN
       D% = VARPTR(A%(49)) / 256
    END IF
    POKE VARPTR(A%(0)) + I%, D%
NEXT I%
CALL ABSOLUTE(VARPTR(A%(0)))
DEF SEG
IF A%(49) = 0 THEN
   PRINT "Please run TX.COM first"
   END
END IF
END SUB

SUB TX (s AS STRING)
PRINT #1, CHR$(14); "["; s; "]";
END SUB

