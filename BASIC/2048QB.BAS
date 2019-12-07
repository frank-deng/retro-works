DEFINT A-Z
COMMON SC#, SL

SC#=0:DIM SHARED B(4,4),S(16,2):SL=0
RANDOMIZE TIMER
COLOR 9
CLS:LOCATE 8,28,0:PRINT CHR$(218);STRING$(21,196);CHR$(191);
FOR I=1 TO 9
  LOCATE 8+I,28:PRINT CHR$(179);SPC(21);CHR$(179);
NEXT I
LOCATE 18,28:PRINT CHR$(192);STRING$(21,196);CHR$(217);
COLOR 14
LOCATE 6,29:PRINT "Score:";

CALL UPDATEBOARD

DO
  K$=INKEY$
  SELECT CASE K$
    CASE CHR$(27) 
      EXIT DO
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

IF SL=0 THEN
  SOUND 100,2
  LOCATE 20,35:COLOR 12:PRINT "GAME OVER";
  WHILE INPUT$(1)<>CHR$(27):WEND
END IF
COLOR 7
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
  COLOR 14
  SL=0:LOCATE 6,35:PRINT SC#;
  COLOR 15
  FOR Y=0 TO 3
    LOCATE (10+Y*2),29
    FOR X=0 TO 3
      IF B(Y,X)<>0 THEN
        PRINT USING "#####";B(Y,X);
      ELSE
        PRINT "    .";
        S(SL,0)=Y:S(SL,1)=X:SL=SL+1
      END IF
    NEXT X
  NEXT Y
  IF SL=0 THEN EXIT SUB

  SE=INT(RND*20) MOD SL
  Y=S(SE,0):X=S(SE,1):B(Y,X)=((INT(RND*10) MOD 2)+1)*2
  LOCATE 10+2*Y,29+5*X:PRINT USING "#####";B(Y,X);
  IF SL>1 THEN EXIT SUB

  FOR Y=0 TO 3:FOR X=0 TO 3
    IF X<3 THEN IF B(Y,X)=B(Y,X+1) THEN EXIT SUB
    IF Y<3 THEN IF B(Y,X)=B(Y+1,X) THEN EXIT SUB
  NEXT X:NEXT Y
  SL=0
END SUB
