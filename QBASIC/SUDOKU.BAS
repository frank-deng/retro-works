DEFINT A-Z
DECLARE FUNCTION GETCAND(X,Y)
DECLARE FUNCTION GETNEXTNUM(N,C)
DECLARE FUNCTION ISFINISHED()
DECLARE FUNCTION PUSH(N,C)
DECLARE FUNCTION POP()
DECLARE SUB PRINTBOARD()
DECLARE SUB UPDATECANDL()

COMMON CANDL,STACKL,STATUS
DIM SHARED BOARD(9,9), CAND(81,3), S(81):SL=0: STATUS=0
' INPUT "Filename: ", F$
F$="sudoku2.txt"
OPEN F$ FOR INPUT AS #1
FOR Y=0 TO 8:FOR X=0 TO 8
  INPUT #1,BOARD(Y,X)
NEXT X:NEXT Y
CLOSE #1

PRINT "Checking sudoku...";: LOCATE ,1

REM Check inconsistent numbers
FOR Y = 0 TO 8: NUMS = 0
  FOR X = 0 TO 8: N = BOARD(Y, X)
    IF N<>0 THEN
      IF (NUMS AND (2^N)) <> 0 THEN
        PRINT "Inconsistent number at row";Y+1:END
      ELSE
        NUMS = NUMS OR (2^N)
      END IF
    END IF
  NEXT X
NEXT Y
  
FOR X = 0 TO 8: NUMS = 0
  FOR Y = 0 TO 8: N = BOARD(Y, X)
    IF N<>0 THEN
      IF (NUMS AND (2^N)) <> 0 THEN
        PRINT "Inconsistent number at column";X+1:END
      ELSE
        NUMS = NUMS OR (2^N)
      END IF
    END IF
  NEXT Y
NEXT X
  
FOR AREA = 0 TO 8
  AX = (AREA MOD 3) * 3: AY = AREA \ 3 * 3: NUMS = 0
  FOR Y = 0 TO 2: FOR X = 0 TO 2
    N = BOARD(AY+Y, AX+X)
    IF N<>0 THEN
      IF (NUMS AND (2^N)) <> 0 THEN
        PRINT "Inconsistent number at area";AREA+1:END
      ELSE
        NUMS = NUMS OR (2^N)
      END IF
    END IF
  NEXT X: NEXT Y
NEXT AREA

PRINT "Checking passed, start calculating...";: LOCATE ,1

REM Check empty cells without answer, and complete cells with only one answer
DO
  CALL UPDATECANDL
  IF CANDL = 0 THEN
    EXIT DO
  END IF
  STATUS = 1
  FOR I = 0 TO CANDL-1
    CN = CAND(I,2)
    IF (CN AND (CN-1))=0 THEN
      X = CAND(I,0): Y = CAND(I,1)
      BOARD(Y,X) = GETNEXTNUM(0, CN)
      STATUS = 0
    END IF
  NEXT I
LOOP WHILE STATUS=0

IF CANDL = 0 THEN
  PRINT "Calculation finished."; TAB(78)
  PRINT ""
  CALL PRINTBOARD: END
END IF

REM Start solving complex puzzles
WHILE ISFINISHED()=0
  X = CAND(SL,0): Y = CAND(SL,1)
  C = GETCAND(X,Y): CAND(SL,2) = C
  IF C=0 THEN
    IF SL = 0 THEN
      PRINT "No answer."; TAB(78): PRINT "": END
    END IF

    S(SL-1) = GETNEXTNUM(N, CAND(SL-1,2))
  ELSE
  END IF
  CALL PRINTBOARD: PRINT ""
WEND
CALL PRINTBOARD
END

FUNCTION ISFINISHED()
  FOR Y=0 TO 8: FOR X=0 TO 8
    IF BOARD(Y,X)=1 THEN
      ISFINISHED = 0
      EXIT FUNCTION
    END IF
  NEXT X: NEXT Y
  ISFINISHED = 1
END FUNCTION

FUNCTION GETCAND(X,Y)
  NUMS = 0
  FOR I = 0 TO 8
    NUMS = NUMS OR (2^BOARD(Y,I)) OR (2^BOARD(I,X))
  NEXT I
  OX = INT(X/3)*3 : OY = INT(Y/3)*3
  FOR I = OY TO OY+2 : FOR J = OX TO OX+2
    NUMS = NUMS OR (2^BOARD(I,J))
  NEXT J : NEXT I
  GETCAND = (NOT NUMS) AND &H3fe
END FUNCTION

FUNCTION GETNEXTNUM(N,C)
  N = N + 1
  WHILE N <= 9
    IF (C AND (2^N)) <> 0 THEN
      GETNEXTNUM = N
      EXIT FUNCTION
    END IF
    N = N + 1
  WEND
  GETNEXTNUM = 0
END FUNCTION

FUNCTION PUSH(N,C)
  X = CAND(SL,0): Y = CAND(SL,1)
  BOARD(Y,X) = N: CAND(SL) = C
  SL = SL + 1
END FUNCTION

FUNCTION POP()
  IF SL = 0 THEN POP = 0: EXIT FUNCTION
  SL = SL-1
  X = CAND(SL,0): Y = CAND(SL,1)
  BOARD(Y,X) = 0
  POP = 1
END FUNCTION

SUB PRINTBOARD()
  FOR Y=0 TO 8
    FOR X=0 TO 8
      PRINT USING "# ";BOARD(Y,X);
      IF (X MOD 3) = 2 THEN PRINT " ";
    NEXT X
    PRINT "": IF (Y MOD 3) = 2 THEN PRINT ""
  NEXT Y
END SUB

SUB UPDATECANDL()
  SHARED CANDL
  CANDL = 0
  FOR Y=0 TO 8:FOR X=0 TO 8
    IF BOARD(Y,X)=0 THEN
      C = GETCAND(X,Y)
      IF C=0 THEN
        PRINT "No answer at row";Y+1;", column";X+1;TAB(79):END
      END IF
      CAND(CANDL,0)=X : CAND(CANDL,1)=Y: CAND(CANDL,2)=C
      CANDL = CANDL + 1
    END IF
  NEXT X:NEXT Y
END SUB
