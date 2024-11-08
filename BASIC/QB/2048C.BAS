DEFINT A-Z
TYPE REGSTYPE
  AX AS INTEGER
  BX AS INTEGER
  CX AS INTEGER
  DX AS INTEGER
  BP AS INTEGER
  SI AS INTEGER
  DI AS INTEGER
  DS AS INTEGER
  ES AS INTEGER
  FLAGS AS INTEGER
END TYPE
DECLARE SUB INTX(N AS INTEGER,REGS AS REGSTYPE)
DECLARE FUNCTION n$ (n%)
DECLARE FUNCTION nd$ (A#)
DECLARE SUB TX (s AS STRING)

DIM SHARED ASMINTX(47),ASMDRAW(44)
COMMON SHARED REGS AS REGSTYPE
COMMON SC#, SL, W, H, X0, Y0
SC#=0:DIM SHARED B(4,4),S(16,2):SL=0
RANDOMIZE TIMER

rem B(3,3)=4096:B(3,2)=2048:B(3,1)=1024:B(3,0)=512:B(2,0)=256:B(2,1)=128
rem B(2,2)=64:B(2,3)=32:B(1,3)=16:B(1,2)=8

DATA &H50,&H53,&H51,&H52,&H55,&H56,&H57,&H1E,&H6,&HBE,&H0,&H0,&HB8,&H0,&H0
DATA &H2E,&H89,&H36,&H58,&H1,&H2E,&HA3,&H5A,&H1,&H8E,&HD8,&HB9,&H9,&H0,&HFF
DATA &H34,&H83,&HC6,&H2,&HE2,&HF9,&H7,&H1F,&H5F,&H5E,&H5D,&H5A,&H59,&H5B,&H58
DATA &HCD,&H0,&H9C,&H6,&H1E,&H57,&H56,&H55,&H52,&H51,&H53,&H50,&H2E,&HA1,&H5A
DATA &H1,&H8E,&HD8,&H2E,&H8B,&H36,&H58,&H1,&HB9,&HA,&H0,&H8F,&H4,&H83,&HC6,&H2
DATA &HE2,&HF9,&H7,&H1F,&H5F,&H5E,&H5D,&H5A,&H59,&H5B,&H58,&HCB
DATA &H0,&H0,&H0,&H0,&H0

DEF SEG = VARSEG(ASMINTX(0)): P = VARPTR(ASMINTX(0))
FOR I = 0 TO 92: READ V: POKE P, V: P = P + 1: NEXT I
DEF SEG
REGS.AX=&HDB00:CALL INTX(&H2F,REGS)
IF (REGS.AX AND 255)<>255 OR REGS.BX<>&H5450 THEN
  PRINT "Please run UCDOS first.":END
END IF
REGS.AX=&H11:CALL INTX(&H79,REGS)
IF (REGS.FLAGS AND &H40)=0 THEN
  PRINT "Please run TX.COM first.": END
END IF
BG=0
REGS.AX=&HFF00:REGS.BX=&HA03:CALL INTX(&H10,REGS)
IF (REGS.AX AND 255)<>255 THEN BG=1

OPEN "LPT3" FOR OUTPUT AS #1
TX("M10CU1,0CO8KB1,0CL0")
TX("CO3B0,0,640,480CO7")

IF BG=1 THEN
  BGW=245:BGH=221
  FOR Y=0 TO (480\BGH)+1:FOR X=0 TO (640\BGW)+1
    TX("RE"+n$(X*BGW)+","+n$(Y*BGH)+",BG.PCX$")
  NEXT X:NEXT Y
END IF

W = 90: H = 90 : X0 = (640-W*4)/2: Y0 = (480-W*4-40)/2+40
CALL DRAWBOX(X0, Y0-40, X0+W*4-1, Y0-1)
TX ("{(0)7@24,24=0-"+n$(X0+6)+"|"+n$(Y0-24-8)+"得分：}")
FOR J=0 TO 3:FOR I=0 TO 3
  CALL DRAWBOX(X0+W*I, Y0+H*J, X0+W*(I+1)-1, Y0+H*(J+1)-1)
NEXT I:NEXT J

CALL UPDATEBOARD
KEY 15,CHR$(128)+CHR$(72):KEY 16,CHR$(128)+CHR$(75)
KEY 17,CHR$(128)+CHR$(77):KEY 18,CHR$(128)+CHR$(80)
ON KEY(11) GOSUB KMOVEUP:ON KEY(12) GOSUB KMOVELEFT
ON KEY(13) GOSUB KMOVERIGHT:ON KEY(14) GOSUB KMOVEDOWN
ON KEY(15) GOSUB KMOVEUP:ON KEY(16) GOSUB KMOVELEFT
ON KEY(17) GOSUB KMOVERIGHT:ON KEY(18) GOSUB KMOVEDOWN
FOR I=11 to 18:KEY(I) ON:NEXT I
ACT=0
DO
  IF INKEY$=CHR$(27) THEN
    EXIT DO
  END IF
  SELECT CASE ACT
    CASE 1:
      ACT=5:CALL MOVEUP
    CASE 2:
      ACT=5:CALL MOVELEFT
    CASE 3:
      ACT=5:CALL MOVERIGHT
    CASE 4:
      ACT=5:CALL MOVEDOWN
  END SELECT
  IF ACT=5 THEN ACT=0
LOOP WHILE SL>0
FOR I=11 to 18:KEY(I) OFF:NEXT I

IF SL=0 THEN
  SOUND 100,2
  TX ("CO7B"+n$((640-32*4)/2-4)+","+n$(Y0+W*2-16-4)+","+n$((640-32*4)/2+32*4+3)+","+n$(Y0+W*2+19))
  TX ("{%0(0)7@32,32=0-"+n$((640-32*4)/2)+"|"+n$(Y0+W*2-16)+"游戏结束}")
  TX ("CO0R"+n$((640-32*4)/2-4)+","+n$(Y0+W*2-16-4)+","+n$((640-32*4)/2+32*4+3)+","+n$(Y0+W*2+19))
  WHILE INPUT$(1)<>CHR$(27):WEND
END IF

TX("KB1,1M3CU1,1")
CLOSE
CLS:END

KMOVEUP:
IF ACT<>5 THEN ACT=1
RETURN

KMOVELEFT:
IF ACT<>5 THEN ACT=2
RETURN

KMOVERIGHT:
IF ACT<>5 THEN ACT=3
RETURN

KMOVEDOWN:
IF ACT<>5 THEN ACT=4
RETURN

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
  SHARED SL, SC#, X0, Y0
  SL=0:
  TX("{-"+n$(X0+6+24*3)+"|"+n$(Y0-24-8)+"%0(0)7@24,24"+CHR$(0)+nd$(SC#)+"}")
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

FUNCTION n$ (A AS INTEGER)
n$ = LTRIM$(RTRIM$(STR$(A)))
END FUNCTION

FUNCTION nd$ (A AS DOUBLE)
nd$ = LTRIM$(RTRIM$(STR$(A)))
END FUNCTION

SUB TX (s AS STRING)
PRINT #1, CHR$(14); "["; s; "]";
END SUB

SUB DRAWBOX(X0 AS INTEGER,Y0 AS INTEGER,X1 AS INTEGER,Y1 AS INTEGER)
  TX("CO7B"+n$(X0+2)+","+n$(Y0+2)+","+n$(X1-2)+","+n$(Y1-2))
  TX("CO15B"+n$(X0)+","+n$(Y0)+","+n$(X1)+","+n$(Y0+1))
  TX("B"+n$(X0)+","+n$(Y0)+","+n$(X0+1)+","+n$(Y1))
  TX("CO8B"+n$(X1-1)+","+n$(Y0)+","+n$(X1)+","+n$(Y1))
  TX("B"+n$(X0)+","+n$(Y1-1)+","+n$(X1)+","+n$(Y1))
  TX("CO15D"+n$(X1-1)+","+n$(Y0)+"D"+n$(X0)+","+n$(Y1-1))
END SUB

FUNCTION TZERO(N0 AS INTEGER)
  STATIC N AS INTEGER, RES AS INTEGER
  RES=0:N=N0
  IF (N AND 255)=0 THEN RES=RES+8:N=N\256
  IF (N AND 15)=0 THEN RES=RES+4:N=N\16
  IF (N AND 3)=0 THEN RES=RES+2:N=N\4
  IF (N AND 1)=0 THEN RES=RES+1
  TZERO=RES
END FUNCTION

SUB DRAWNUM(X,Y,N)
  SHARED W, H, X0, Y0
  TX("CO7B"+n$(X0+X*W+3)+","+n$(Y0+Y*H+3)+","+n$(X0+X*W+W-3)+","+n$(Y0+Y*H+H-3))
  IF N>0 THEN
    text$ = n$(N): tl = len(text$)
    ya = (H-32)/2
    IF N<100 THEN
      TX("{@32,48}")
      xa = (W-24*tl)/2
    ELSE
      TX("{@32,32}")
      xa = (W-16*tl)/2
    END IF
    X$ = n$(X0+X*W+xa-1)
    Y$ = n$(Y0+Y*H+ya-1)
    TX("{%1(15-"+X$+"|"+Y$+CHR$(0)+text$+"}")
    X$ = n$(X0+X*W+xa+1)
    Y$ = n$(Y0+Y*H+ya+1)
    TX("{%1(0-"+X$+"|"+Y$+CHR$(0)+text$+"}")
    X$ = n$(X0+X*W+xa)
    Y$ = n$(Y0+Y*H+ya)
    CL$=MID$("991133226548888",TZERO(N),1)
    TX("{%1("+CL$+"-"+X$+"|"+Y$+CHR$(0)+text$+"}")
  END IF
END SUB

SUB INTX (N AS INTEGER, REGS AS REGSTYPE)
  STATIC DS AS INTEGER,SI AS INTEGER,P AS INTEGER
  DS=VARSEG(REGS):SI=VARPTR(REGS)
  DEF SEG=VARSEG(DS):P=VARPTR(DS):DS0=PEEK(P): DS1=PEEK(P+1)
  DEF SEG=VARSEG(SI):P=VARPTR(SI):SI0=PEEK(P): SI1=PEEK(P+1)
  DEF SEG=VARSEG(ASMINTX(0)): P=VARPTR(ASMINTX(0))
  POKE P+&H2E,N
  POKE P+&HA,SI0:POKE P+&HB,SI1
  POKE P+&HD,DS0:POKE P+&HE,DS1
  CALL ABSOLUTE(P)
  DEF SEG
END SUB

