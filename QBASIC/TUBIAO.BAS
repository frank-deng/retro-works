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
s# = 0: MAX# = 0: C = 0: TL = 0: DIM D(128) AS DOUBLE, T(128) AS STRING
COL = 15: BG = 0: RADIUS = 200

INPUT "请输入文件名：", F$
OPEN F$ FOR INPUT AS #2
WHILE NOT EOF(2)
  INPUT #2, T(C), D(C)
  TL0 = LEN(T(C))
  IF TL0 > TL THEN
    TL = TL0
  END IF
  IF C = 0 THEN
    MAX# = D(C)
  ELSEIF D(C) > MAX# THEN
    MAX# = D(C)
  END IF
  s# = s# + D(C): C = C + 1
WEND
CLOSE #2

OPEN "LPT3" FOR OUTPUT AS #1
TX ("M10CU1,0KB1,0CL0CO" + n$(BG) + "B0,0,640,480")
TX ("{=0%1@16,16}")

FOR I = 0 TO C - 1
  TX ("{(" + n$(COL) + "}")
  CALL DrawText(8, I * 17 + 8, T(I))
  CALL DrawBar(TL * 8 + 12, I * 17 + 8, 640 - TL * 8 - 20, D(I) / MAX#, D(I) / s#, D(I))
NEXT I

WHILE INPUT$(1) = "": WEND

' Start drawing pie chart
TX ("CL0CO"+n$(BG)+"B0,0,640,480CO7")

SANGLE = 0
FOR I=0 TO C-2
  ANGLE = SANGLE+FIX(D(I)/S#*360)
  COL = (I mod 13)+2
  CALL DrawPie(430, 240, SANGLE, ANGLE, COL)
  SANGLE=ANGLE
NEXT I
CALL DrawPie(430, 240, SANGLE, 360, 1)

TX ("{(15@16,16}")
LH = 18
TOP = (480-C*LH)/2
FOR I=0 TO C-1
  COL = (I mod 13)+2
  IF I=C-1 THEN
    COL = 1
  END IF
  TX ("CO"+n$(COL)+"B5,"+n$(i*LH+TOP)+","+n$(5+15)+","+n$(i*LH+TOP+15))
  CALL DrawText(5+16+6,I*LH+TOP,T(I)+"（"+percent$(D(I)/s#)+"）")
NEXT I

WHILE INPUT$(1) = "": WEND
TX ("KB1,1M3CU1,1")
CLOSE
END

SUB DrawPie(x as integer,y as integer, sangle as integer, angle as integer, col as integer)
  SHARED RADIUS
  IF sangle <> angle then
    TX("CO"+n$(col)+"E" + n$(x) + "," + n$(y)+","+n$(sangle)+","+n$(angle)+","+n$(RADIUS)+","+n$(RADIUS)+",2,"+n$(col))
  end if
END SUB

SUB DrawBar (x AS INTEGER, y AS INTEGER, w AS INTEGER, l AS SINGLE, pc AS DOUBLE, v as DOUBLE)
  SHARED COL, BG
  TX ("CO" + n$(COL) + "B" + n$(x) + "," + n$(y) + "," + n$(FIX(x + w * l)) + "," + n$(y + 15))
  SN$ = nd$(v)+"（"+percent$(pc)+"）"
  SNL = LEN(SN$) * 8
  IF l < .5 THEN
    TX ("{(" + n$(COL) + "}"): CALL DrawText(x + w * l + 8, y, SN$)
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

FUNCTION percent$ (A AS DOUBLE)
  percent$ = n$(FIX(A * 100)) + "." + n$(FIX(A * 10000) MOD 100) + "％"
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

