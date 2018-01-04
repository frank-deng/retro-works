DEFINT A-Z
DECLARE SUB TestTX ()
DECLARE FUNCTION n$ (n%)
DECLARE FUNCTION nd$ (A#)
DECLARE SUB TX (s AS STRING)
COMMON SC#, SL

SC#=0:DIM SHARED B(4,4),S(16,2):SL=0
RANDOMIZE TIMER

CALL TestTX
OPEN "LPT3" FOR OUTPUT AS #1
TX("M10CU1,0CO8KB1,0CL0")
TX("CL0CO0B0,0,640,480CO7")
TX ("{(7@24,24=0-240|40???}")

CALL UPDATEBOARD

DO
  K$=INKEY$
  SELECT CASE K$
    CASE CHR$(27) 
      CLS:END
    CASE CHR$(0)+CHR$(72)
      CALL MOVEUP
    CASE CHR$(0)+CHR$(75)
      CALL MOVELEFT
    CASE CHR$(0)+CHR$(77)
      CALL MOVERIGHT
    CASE CHR$(0)+CHR$(80)
      CALL MOVEDOWN
  END SELECT
LOOP WHILE SL>0
LOCATE 20,35:PRINT "GAME OVER";
WHILE INPUT$(1)<>CHR$(27):WEND

TX("KB1,1M3CU1,1")
CLOSE
CLS:END

SUB MOVEUP
  SHARED SL, SC#
  M=0
  FOR X=0 TO 3
    Y0=0:Y=1
    WHILE Y<=3
      IF B(Y0,X)=0 THEN
        IF B(Y,X)<>0 THEN
          B(Y0,X)=B(Y,X):B(Y,X)=0
          M=1
        END IF
        Y=Y+1
      ELSE
        IF B(Y,X)=0 THEN
          Y=Y+1
        ELSEIF B(Y0,X)=B(Y,X) THEN
          SC#=SC#+B(Y,X)
          B(Y0,X)=B(Y0,X)*2:B(Y,X)=0
          Y0=Y0+1:Y=Y+1
          M=1
        ELSE
          Y0=Y0+1
          IF Y0=Y THEN Y=Y+1
        END IF
      END IF
    WEND
  NEXT X
  IF M=1 THEN CALL UPDATEBOARD
END SUB

SUB MOVELEFT
  SHARED SL, SC#
  M=0
  FOR Y=0 TO 3
    X0=0:X=1
    WHILE X<=3
      IF B(Y,X0)=0 THEN
        IF B(Y,X)<>0 THEN
          B(Y,X0)=B(Y,X):B(Y,X)=0
          M=1
        END IF
        X=X+1
      ELSE
        IF B(Y,X)=0 THEN
          X=X+1
        ELSEIF B(Y,X0)=B(Y,X) THEN
          SC#=SC#+B(Y,X)
          B(Y,X0)=B(Y,X0)*2:B(Y,X)=0
          X0=X0+1:X=X+1
          M=1
        ELSE
          X0=X0+1
          IF X0=X THEN X=X+1
        END IF
      END IF
    WEND
  NEXT Y
  IF M=1 THEN CALL UPDATEBOARD
END SUB

SUB MOVERIGHT
  SHARED SL, SC#
  M=0
  FOR Y=0 TO 3
    X0=3:X=2
    WHILE X>=0
      IF B(Y,X0)=0 THEN
        IF B(Y,X)<>0 THEN
          B(Y,X0)=B(Y,X):B(Y,X)=0
          M=1
        END IF
        X=X-1
      ELSE
        IF B(Y,X)=0 THEN
          X=X-1
        ELSEIF B(Y,X0)=B(Y,X) THEN
          SC#=SC#+B(Y,X)
          B(Y,X0)=B(Y,X0)*2:B(Y,X)=0
          X0=X0-1:X=X-1
          M=1
        ELSE
          X0=X0-1
          IF X0=X THEN X=X-1
        END IF
      END IF
    WEND
  NEXT Y
  IF M=1 THEN CALL UPDATEBOARD
END SUB

SUB MOVEDOWN
  SHARED SL, SC#
  M=0
  FOR X=0 TO 3
    Y0=3:Y=2
    WHILE Y>=0
      IF B(Y0,X)=0 THEN
        IF B(Y,X)<>0 THEN
          B(Y0,X)=B(Y,X):B(Y,X)=0
          M=1
        END IF
        Y=Y-1
      ELSE
        IF B(Y,X)=0 THEN
          Y=Y-1
        ELSEIF B(Y0,X)=B(Y,X) THEN
          SC#=SC#+B(Y,X)
          B(Y0,X)=B(Y0,X)*2:B(Y,X)=0
          Y0=Y0-1:Y=Y-1
          M=1
        ELSE
          Y0=Y0-1
          IF Y0=Y THEN Y=Y-1
        END IF
      END IF
    WEND
  NEXT X
  IF M=1 THEN CALL UPDATEBOARD
END SUB

SUB UPDATEBOARD()
  SHARED SL, SC#
  SL=0:
  TX("{-320|40"+CHR$(0)+nd$(SC#)+"}")
  FOR Y=0 TO 3
    FOR X=0 TO 3
      IF B(Y,X)<>0 THEN
        CALL DRAWNUM(X,Y,B(Y,X))
      ELSE
        CALL DRAWNUM(X,Y,0)
        S(SL,0)=Y:S(SL,1)=X:SL=SL+1
      END IF
    NEXT X
  NEXT Y
  IF SL=0 THEN EXIT SUB

  SE=INT(RND*20) MOD SL
  Y=S(SE,0):X=S(SE,1):B(Y,X)=((INT(RND*10) MOD 2)+1)*2
  CALL DRAWNUM(X,Y,B(Y,X))
  IF SL>1 THEN EXIT SUB

  FOR Y=0 TO 3:FOR X=0 TO 3
    IF X<3 THEN IF B(Y,X)=B(Y,X+1) THEN EXIT SUB
    IF Y<3 THEN IF B(Y,X)=B(Y+1,X) THEN EXIT SUB
  NEXT X:NEXT Y
  SL=0
END SUB

DATA &H50,&H53,&H56,&HBE,&H00,&H00,&H2E,&HC7,&H04,&H00,&H00,&HB8,&H00,&HDB,&HCD,&H2F
DATA &H3C,&HFF,&H75,&H12,&H81,&HFB,&H50,&H54,&H75,&H0C,&HB8,&H11,&H00,&HCD,&H79,&H75
DATA &H05,&h2E,&HC7,&H04,&H01,&H00,&H5E,&H5B,&H58,&HCB

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

FUNCTION n$ (A AS INTEGER)
n$ = LTRIM$(RTRIM$(STR$(A)))
END FUNCTION

FUNCTION nd$ (A AS DOUBLE)
nd$ = LTRIM$(RTRIM$(STR$(A)))
END FUNCTION

SUB TX (s AS STRING)
PRINT #1, CHR$(14); "["; s; "]";
END SUB

SUB DRAWNUM(X,Y,N)
  X0 = 120: Y0 = 64: W = 60: H = 24
  TX("CO0B"+n$(X0+X*W)+","+n$(Y0+Y*H)+","+n$(X0+X*W+W)+","+n$(Y0+Y*H+H))
  TX("{-"+n$(X0+X*W)+"|"+n$(Y0+Y*H)+CHR$(0)+n$(N)+"}")
END SUB
