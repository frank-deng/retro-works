SUBDEF UPDATEBOARD()
SUBDEF MOVEUP()
SUBDEF MOVELEFT()
SUBDEF MOVERIGHT()
SUBDEF MOVEDOWN()
SUBDEF PRINTNUM(INTEGER X, INTEGER Y, INTEGER N)

INTEGER B(4,4),S(16,2)
INTEGER SL,R,I,DIR
FLOAT SC
STRING K

SC=0:SL=0
RANDOMIZE VAL RIGHT$(TIME$,2)

CURSORTYPE 0
CLS
LOCATE 26,7
PRINT chr$(&H86);chr$(&Hae);
FOR I=0 to 10
  PRINT chr$(&H86);chr$(&Ha2);
NEXT
PRINT chr$(&H86);chr$(&Hb2);

FOR I=1 TO 9
  LOCATE 26,7+I:PRINT chr$(&H86);chr$(&Ha4);SPC(21);chr$(&H86);chr$(&Ha4);
NEXT

LOCATE 26,17
PRINT chr$(&H86);chr$(&Hb6);
FOR I=0 to 10
  PRINT chr$(&H86);chr$(&Ha2);
NEXT
PRINT chr$(&H86);chr$(&Hba);

LOCATE 29,5:PRINT "得点：";

CALL UPDATEBOARD()

R = 1
DIR = 0
WHILE SL>0 AND R>0
  K=INKEY$
  IF DIR=1 THEN
    SELECT CASE K
      CASE "H"
        CALL MOVEUP()
      CASE "K"
        CALL MOVELEFT()
      CASE "M"
        CALL MOVERIGHT()
      CASE "P"
        CALL MOVEDOWN()
      CASE ELSE
    ENDSELECT
    DIR = 0
  ELSE
    SELECT CASE K
      CASE CHR$(27) 
        R=0
      CASE CHR$(255) 
        DIR = 1
      CASE ELSE
    ENDSELECT
  ENDIF
WEND

IF SL=0 THEN
  LOCATE 33,19:PRINT "ゲームオーバー";
  WHILE INPUT$(1)<>CHR$(27):WEND
ENDIF
CLS:END

SUB MOVEUP()
  INTEGER M,X,Y,X0,Y0
  M=0
  FOR X=0 TO 3
    Y0=0:Y=1
    WHILE Y<=3
      IF B(Y0,X)=0 THEN
        IF B(Y,X)<>0 THEN
          B(Y0,X)=B(Y,X):B(Y,X)=0
          M=1
        ENDIF
        Y=Y+1
      ELSE
        IF B(Y,X)=0 THEN
          Y=Y+1
        ELSEIF B(Y0,X)=B(Y,X) THEN
          SC=SC+B(Y,X)
          B(Y0,X)=B(Y0,X)*2:B(Y,X)=0
          Y0=Y0+1:Y=Y+1
          M=1
        ELSE
          Y0=Y0+1
          IF Y0=Y THEN Y=Y+1
        ENDIF
      ENDIF
    WEND
  NEXT
  IF M=1 THEN CALL UPDATEBOARD()
ENDSUB

SUB MOVELEFT()
  INTEGER M,X,Y,X0,Y0
  M=0
  FOR Y=0 TO 3
    X0=0:X=1
    WHILE X<=3
      IF B(Y,X0)=0 THEN
        IF B(Y,X)<>0 THEN
          B(Y,X0)=B(Y,X):B(Y,X)=0
          M=1
        ENDIF
        X=X+1
      ELSE
        IF B(Y,X)=0 THEN
          X=X+1
        ELSEIF B(Y,X0)=B(Y,X) THEN
          SC=SC+B(Y,X)
          B(Y,X0)=B(Y,X0)*2:B(Y,X)=0
          X0=X0+1:X=X+1
          M=1
        ELSE
          X0=X0+1
          IF X0=X THEN X=X+1
        ENDIF
      ENDIF
    WEND
  NEXT
  IF M=1 THEN CALL UPDATEBOARD()
ENDSUB

SUB MOVERIGHT()
  INTEGER M,X,Y,X0,Y0
  M=0
  FOR Y=0 TO 3
    X0=3:X=2
    WHILE X>=0
      IF B(Y,X0)=0 THEN
        IF B(Y,X)<>0 THEN
          B(Y,X0)=B(Y,X):B(Y,X)=0
          M=1
        ENDIF
        X=X-1
      ELSE
        IF B(Y,X)=0 THEN
          X=X-1
        ELSEIF B(Y,X0)=B(Y,X) THEN
          SC=SC+B(Y,X)
          B(Y,X0)=B(Y,X0)*2:B(Y,X)=0
          X0=X0-1:X=X-1
          M=1
        ELSE
          X0=X0-1
          IF X0=X THEN X=X-1
        ENDIF
      ENDIF
    WEND
  NEXT
  IF M=1 THEN CALL UPDATEBOARD()
ENDSUB

SUB MOVEDOWN()
  INTEGER M,X,Y,X0,Y0
  M=0
  FOR X=0 TO 3
    Y0=3:Y=2
    WHILE Y>=0
      IF B(Y0,X)=0 THEN
        IF B(Y,X)<>0 THEN
          B(Y0,X)=B(Y,X):B(Y,X)=0
          M=1
        ENDIF
        Y=Y-1
      ELSE
        IF B(Y,X)=0 THEN
          Y=Y-1
        ELSEIF B(Y0,X)=B(Y,X) THEN
          SC=SC+B(Y,X)
          B(Y0,X)=B(Y0,X)*2:B(Y,X)=0
          Y0=Y0-1:Y=Y-1
          M=1
        ELSE
          Y0=Y0-1
          IF Y0=Y THEN Y=Y-1
        ENDIF
      ENDIF
    WEND
  NEXT
  IF M=1 THEN CALL UPDATEBOARD()
ENDSUB

SUB UPDATEBOARD()
  INTEGER X,Y,SE
  SL=0:LOCATE 35,5:PRINT SC;
  FOR Y=0 TO 3
    FOR X=0 TO 3
      CALL PRINTNUM(X,Y,B(Y,X))
      IF B(Y,X)=0 THEN
        S(SL,0)=Y:S(SL,1)=X:SL=SL+1
      ENDIF
    NEXT
  NEXT
  IF SL=0 THEN RETURN

  SE=INT(RND(20)) MOD SL
  X=S(SE,1) : Y=S(SE,0)
  B(Y,X)=((INT(RND(10)) MOD 2)+1)*2
  CALL PRINTNUM(X,Y,B(Y,X))
  IF SL>1 THEN RETURN

  FOR Y=0 TO 3
    FOR X=0 TO 3
      IF X<3 THEN
        IF B(Y,X)=B(Y,X+1) THEN
          RETURN
        ENDIF
      ENDIF
      IF Y<3 THEN
        IF B(Y,X)=B(Y+1,X) THEN
          RETURN
        ENDIF
      ENDIF
    NEXT
  NEXT
  SL=0
ENDSUB

SUB PRINTNUM(INTEGER X, INTEGER Y, INTEGER N)
  STRING ST
  ST = STR$(N)
  LOCATE 29+5*X,9+2*Y
  PRINT SPC(5);
  IF N<>0 THEN
    LOCATE 29+5*(X+1)-LEN(ST),9+2*Y
    PRINT ST;
  ELSE
    LOCATE 29+5*X,9+2*Y
    PRINT "    .";
  ENDIF
ENDSUB

