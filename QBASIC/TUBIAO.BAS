DECLARE SUB TestTX ()
DECLARE FUNCTION n$ (n%)
DECLARE SUB TX (s AS STRING)
DECLARE SUB DrawText(x as integer,y as integer,text as string)
DECLARE SUB DrawBar(x as integer,y as integer, w as integer, l as single, percent as double)
DATA &H50,&H53,&H56,&HBE,&H00,&H00,&H2E,&HC7,&H04,&H00,&H00,&HB8,&H00,&HDB,&HCD,&H2F
DATA &H3C,&HFF,&H75,&H12,&H81,&HFB,&H50,&H54,&H75,&H0C,&HB8,&H11,&H00,&HCD,&H79,&H75
DATA &H05,&h2E,&HC7,&H04,&H01,&H00,&H5E,&H5B,&H58,&HCB

DEFINT A-Z : COMMON COL, BG
TestTX

' Prepare data
S#=0:MAX#=0:C=0:TL=0:DIM D(128) AS DOUBLE, T(128) AS STRING
COL = 15: BG = 0

INPUT "请输入文件名：",F$
OPEN F$ FOR INPUT AS #2
WHILE NOT EOF(2)
  INPUT #2,T(C),D(C)
  TL0 = LEN(T(C))
  IF TL0 > TL THEN
    TL = TL0
  END IF
  IF C=0 THEN
    MAX#=D(C)
  ELSEIF D(C)>MAX# THEN
    MAX#=D(C)
  END IF
  S#=S#+D(C):C=C+1
WEND
CLOSE #2

OPEN "LPT3" FOR OUTPUT AS #1
TX ("M18CU1,0KB1,0CL0CO"+n$(BG)+"B0,0,640,480")
TX ("{=0%1@16,16}")

FOR I=0 TO C-1
  TX ("{("+n$(COL)+"}")
  CALL DrawText(0, I*17+8, T(I))
  CALL DrawBAR(TL*8+4, I*17+8, 640-TL*8-4, D(I)/MAX#, D(I)/S#)
NEXT I

WHILE INPUT$(1) = "": WEND
TX ("KB1,1M3CU1,1")
CLOSE
END

FUNCTION n$ (A AS INTEGER)
n$ = LTRIM$(RTRIM$(STR$(A)))
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

SUB DrawText(x as integer,y as integer,text as string)
  TX ("{-" + n$(x) + "|" + n$(y) + CHR$(0) +text+"}")
END SUB

SUB DrawBar(x as integer,y as integer, w as integer, l as single, percent as double)
  SHARED COL, BG
  TX ("CO"+n$(COL)+"B"+n$(x)+","+n$(y)+","+n$(fix(x+w*l))+","+n$(y+15))
  SN$ = n$(FIX(percent*100))+"."+n$(FIX(percent*10000) mod 100)+"％": SNL = LEN(SN$)*8
  IF l < 0.5 then
    TX ("{("+n$(COL)+"}"): CALL DrawText(x+w*l+4, y, SN$)
  ELSE
    TX ("{("+n$(BG)+"}"): CALL DrawText(x+w*l-SNL-4, y, SN$)
  END IF
END SUB