DECLARE FUNCTION COMP% (M0%, N0%)
DECLARE FUNCTION CHECK% (N0%)
DEFINT A-Z
DIM SHARED BITMASK(15)
FOR I = 0 TO 14: BITMASK(I) = 2 ^ I: NEXT I

DIM G(8, 2): L = 0
PRINT "Hint: Enter "; CHR$(34); "0,0,0"; CHR$(34); " to start calculation."
DO
  INPUT "Guess,A,B:", IG, A, B
  IF IG = 0 THEN
    EXIT DO
  ELSEIF CHECK(IG) = 0 OR A < 0 OR A > 3 OR B < 0 OR B > 4 OR A + B > 4 THEN
    PRINT "Invalid Input!"
  ELSE
    G(L, 0) = IG: G(L, 1) = A * 10 + B: L = L + 1
  END IF
LOOP WHILE L < 8
IF L <= 0 THEN END

PRINT "": PRINT "Calculation started, press Esc to cancel."
FOR N = 123 TO 9876 STEP 1
  IF CHR$(27) = INKEY$ THEN
    PRINT "": PRINT "Calculation Cancelled."
    END
  END IF
  PASSED = 1
  FOR I = 0 TO L - 1 STEP 1
    IF COMP(N, G(I, 0)) <> G(I, 1) THEN
      PASSED = 0
      EXIT FOR
    END IF
  NEXT I
  IF PASSED = 1 THEN
    IF N <= 999 THEN
      PRINT " 0"; : PRINT USING "###"; N;
    ELSE
      PRINT USING "#####"; N;
    END IF
  END IF
NEXT N
PRINT "": PRINT "Calculation Finished."

FUNCTION CHECK (NP)
  STATIC I, J, DUP, N0
  N0 = NP
  IF N0 < 123 OR N0 > 9876 THEN
    CHECK = 0: EXIT FUNCTION
  END IF
  DUP = 0
  FOR I = 0 TO 3
    DN = (N0 MOD 10): N0 = N0 \ 10
    IF (DUP AND BITMASK(DN)) <> 0 THEN
      CHECK = 0: EXIT FUNCTION
    END IF
    DUP = DUP OR BITMASK(DN)
  NEXT I
  CHECK = 1
END FUNCTION

FUNCTION COMP (MP, NP)
  STATIC I, M0, N0, DM, DN, BITM, BITN, DUP, RES
  DIM M(4): DIM N(4)
  RES = 0: DUP = 0: M0 = MP: N0 = NP
  REM Extract digits from two numbers
  FOR I = 0 TO 3
    DM = (M0 MOD 10): M0 = M0 \ 10
    REM Check M0 for duplicated digits while N0 has already been checked during input
    IF (DUP AND BITMASK(DM)) <> 0 THEN
      COMP = -1: EXIT FUNCTION
    END IF
    DUP = DUP OR BITMASK(DM)
    M(I) = DM: N(I) = (N0 MOD 10): N0 = N0 \ 10
  NEXT I
  BITM = 0: BITN = 0
  FOR I = 0 TO 3
    DM = M(I): DN = N(I)
    IF DM = DN THEN
      RES = RES + 10
    ELSE
      BITM = BITM OR BITMASK(DM)
      BITN = BITN OR BITMASK(DN)
    END IF
  NEXT I
  I = BITM AND BITN
  WHILE I <> 0
    RES = RES + 1
    I = I AND (I - 1)
  WEND
  COMP = RES
END FUNCTION

