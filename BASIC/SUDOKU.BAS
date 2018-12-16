DEFINT A-Z
DECLARE FUNCTION GETCAND(X,Y)
DECLARE FUNCTION GETNEXTNUM(N,C)
DECLARE FUNCTION ISFINISHED()
DECLARE SUB PRINTBOARD()
DECLARE SUB UPDATECANDL()

COMMON CANDL,STATUS
DIM SHARED BOARD(9,9), CAND(81,3), BITMASK(15): STATUS = 0
FOR I = 0 TO 14
  BITMASK(I) = 2^I
NEXT I

PRINT "Input sudoku":DIM B(9)
FOR Y=0 TO 8:
  PRINT Y+1;:INPUT ": ",B(0),B(1),B(2),B(3),B(4),B(5),B(6),B(7),B(8)
  FOR X=0 TO 8
    BOARD(Y,X)=B(X)
    IF BOARD(Y,X) > 9 OR BOARD(Y,X) < 0 THEN
      PRINT "Invalid number at row";Y+1;", column";X+1: END
    END IF
  NEXT X
NEXT Y

PRINT "Checking sudoku... ";

REM Check inconsistent numbers
FOR Y = 0 TO 8: NUMS = 0
  FOR X = 0 TO 8: N = BOARD(Y, X)
    IF N<>0 THEN
      IF (NUMS AND BITMASK(N)) <> 0 THEN
        PRINT "Inconsistent number at row";Y+1:END
      ELSE
        NUMS = NUMS OR BITMASK(N)
      END IF
    END IF
  NEXT X
NEXT Y
  
FOR X = 0 TO 8: NUMS = 0
  FOR Y = 0 TO 8: N = BOARD(Y, X)
    IF N<>0 THEN
      IF (NUMS AND BITMASK(N)) <> 0 THEN
        PRINT "Inconsistent number at column";X+1:END
      ELSE
        NUMS = NUMS OR BITMASK(N)
      END IF
    END IF
  NEXT Y
NEXT X
  
FOR AREA = 0 TO 8
  AX = (AREA MOD 3) * 3: AY = (AREA \ 3) * 3: NUMS = 0
  FOR Y = 0 TO 2: FOR X = 0 TO 2
    N = BOARD(AY+Y, AX+X)
    IF N<>0 THEN
      IF (NUMS AND BITMASK(N)) <> 0 THEN
        PRINT "Inconsistent number at area";AREA+1:END
      ELSE
        NUMS = NUMS OR BITMASK(N)
      END IF
    END IF
  NEXT X: NEXT Y
NEXT AREA

REM Check empty cells without answer, and complete cells with only one answer
CALL UPDATECANDL : PRINT "Passed"
PRINT "Calculation started, press Esc to cancel.";: LOCATE ,1
DO
  STATUS = 1
  FOR I = 0 TO CANDL-1
    CN = CAND(I,2)
    IF (CN AND (CN-1))=0 THEN
      X = CAND(I,0): Y = CAND(I,1)
      BOARD(Y,X) = GETNEXTNUM(0,CN)
      STATUS = 0
    END IF
  NEXT I
  IF STATUS = 0 THEN CALL UPDATECANDL
LOOP WHILE STATUS=0 AND CANDL>0

IF CANDL = 0 THEN
  PRINT "Calculation finished."; TAB(78): PRINT ""
  CALL PRINTBOARD: END
END IF

REM Start solving complex puzzles
DIM S(81): SL=0: S(0) = GETNEXTNUM(0, CAND(0,2))
WHILE SL < CANDL AND INKEY$<>CHR$(27)
  X = CAND(SL,0): Y = CAND(SL,1)
  IF S(SL) = 0 THEN
    BOARD(Y,X) = 0: SL = SL - 1
    IF SL = -1 THEN
      PRINT "No answer."; TAB(78): PRINT ""
      END
    END IF
    S(SL) = GETNEXTNUM(S(SL), CAND(SL,2))
  ELSEIF CHECKNUM(X,Y,S(SL))=1 THEN
    BOARD(Y,X) = S(SL) : SL = SL + 1
    IF SL < CANDL THEN
      S(SL) = GETNEXTNUM(0, CAND(SL,2))
    ELSE
      STATUS = 2
    END IF
  ELSE
    S(SL) = GETNEXTNUM(S(SL), CAND(SL,2))
  END IF
WEND

IF STATUS = 2 THEN
  PRINT "Calculation finished."; TAB(78): PRINT ""
  CALL PRINTBOARD
ELSE
  PRINT "Calculation cancelled."; TAB(78): PRINT ""
END IF
END

REM Functions and SUBs
FUNCTION GETCAND(X,Y)
  NUMS = 0
  FOR I = 0 TO 8
    NUMS = NUMS OR (2^BOARD(Y,I)) OR (2^BOARD(I,X))
  NEXT I
  OX = (X \ 3) * 3: OY = (Y \ 3) * 3
  FOR I = OY TO OY+2 : FOR J = OX TO OX+2
    NUMS = NUMS OR (2^BOARD(I,J))
  NEXT J : NEXT I
  GETCAND = (NOT NUMS) AND &H3fe
END FUNCTION

FUNCTION GETNEXTNUM(N,C)
  N = N + 1
  WHILE N <= 9
    IF (C AND BITMASK(N)) <> 0 THEN
      GETNEXTNUM = N
      EXIT FUNCTION
    END IF
    N = N + 1
  WEND
  GETNEXTNUM = 0
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

FUNCTION CHECKNUM(X,Y,N)
  FOR I = 0 TO 8
    IF X<>I AND BOARD(Y,I)=N THEN
      CHECKNUM = 0: EXIT FUNCTION
    ELSEIF Y<>I AND BOARD(I,X)=N THEN
      CHECKNUM = 0: EXIT FUNCTION
    END IF
  NEXT I
  AX = (X \ 3) * 3: AY = (Y \ 3) * 3
  FOR Y1 = AY TO AY+2: FOR X1 = AX TO AX+2
    IF X1<>X AND Y1<>Y AND BOARD(Y1,X1)=N THEN CHECKNUM = 0: EXIT FUNCTION
  NEXT X1: NEXT Y1
  CHECKNUM = 1
END FUNCTION

SUB UPDATECANDL()
  SHARED CANDL
  CANDL = 0
  FOR Y=0 TO 8:FOR X=0 TO 8
    IF BOARD(Y,X)=0 THEN
      C = GETCAND(X,Y)
      IF C=0 THEN PRINT "No answer at row";Y+1;", column";X+1: END
      CAND(CANDL,0)=X : CAND(CANDL,1)=Y: CAND(CANDL,2)=C
      CANDL = CANDL + 1
    END IF
  NEXT X:NEXT Y
END SUB
