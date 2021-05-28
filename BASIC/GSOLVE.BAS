DEFINT A-Z

FUNCTION COMP(M,N)
  STATIC I,J,A,B
  A = 0 : B = 0
  FOR I = 0 TO 3 STEP 1
    IF (M\(10^I) MOD 10) = (N\(10^I) MOD 10) THEN
      A = A+1
    ELSE
      FOR J = 0 TO 3 STEP 1
        IF (I<>J) AND ((M\(10^I) MOD 10) = (N\(10^J) MOD 10)) THEN
          B = B+1
        END IF
      NEXT J
    END IF
  NEXT I
  COMP = A * 10 + B
END FUNCTION

FUNCTION CHECK(N)
  STATIC I,J
  IF N<123 OR N>9876 THEN
    CHECK = 0 : EXIT FUNCTION
  END IF
  FOR I = 0 TO 2 STEP 1
    FOR J = I+1 TO 3 STEP 1
      IF (N\(10^I) MOD 10) = (N\(10^J) MOD 10) THEN
        CHECK = 0 : EXIT FUNCTION
      END IF
    NEXT J
  NEXT I
  CHECK = 1
END FUNCTION

DIM G(8,2) : L=0
PRINT "Hint: Enter ";CHR$(34);"0,0,0";CHR$(34);" to start calculation."
DO
  INPUT "Guess,A,B:",IG,A,B
  IF IG=0 THEN
    EXIT DO
  ELSEIF CHECK(IG)=0 OR A<0 OR A>3 OR B<0 OR B>4 OR A+B>4 THEN
    PRINT "Invalid Input!"
  ELSE
    G(L,0)=IG : G(L,1)=A*10+B : L=L+1
  END IF
LOOP WHILE L<8
IF L<=0 THEN END

PRINT "":PRINT "Calculation started, press Esc to cancel."
FOR N = 123 TO 9876 STEP 1
  IF CHR$(27)=INKEY$ THEN
    PRINT "":PRINT "Calculation Cancelled."
    END
  END IF
  IF CHECK(N)=1 THEN
    PASSED = 1
    FOR I = 0 TO L-1 STEP 1
      IF COMP(N,G(I,0)) <> G(I,1) THEN
        PASSED = 0
        EXIT FOR
      END IF
    NEXT I
    IF PASSED = 1 THEN
      IF N<=999 THEN
        PRINT " 0";:PRINT USING "###";N;
      ELSE
        PRINT USING "#####";N;
      END IF
    END IF
  END IF
NEXT N
PRINT "":PRINT "Calculation Finished."
