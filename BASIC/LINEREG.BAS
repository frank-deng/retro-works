DEFDBL A-Z : DEFINT I
COMMON LENGTH
PRINT ""
PRINT "*** Linear Regression Demo ***"
PRINT ""

REM Read data
INPUT "CSV Filename: ", F$
LENGTH = 0
OPEN F$ FOR INPUT AS #1
WHILE NOT EOF(1)
  INPUT #1,A#,B#
  LENGTH = LENGTH+1
WEND
CLOSE #1
REDIM SHARED X(LENGTH) AS DOUBLE
REDIM SHARED Y(LENGTH) AS DOUBLE
OPEN F$ FOR INPUT AS #1
FOR I=0 TO LENGTH-1
  INPUT #1,X(I),Y(I)
NEXT I
CLOSE #1

REM Start Calculation
T0 = 0 : T1 = 0 : J0 = 1 : J1 = 1
WHILE ABS(J0)>0.0001 OR ABS(J1)>0.0001
  A = 1 : B = 0 : D = 0 : J0 = 0 : J1 = 0
  FOR I = 0 TO LENGTH-1
    B = B + X(I)
    D = D + X(I) * X(I)
    H = T0 + T1 * X(I)
    J0 = J0 + (H - Y(I))
    J1 = J1 + (H - Y(I)) * X(I)
  NEXT I
  B = B / LENGTH : C = B : D = D / LENGTH
  J0 = J0 / LENGTH : J1 = J1 / LENGTH

  DET = 1 / (A*D-B*C)
  A1 = DET * D : B1 = DET * (-B)
  C1 = DET * (-C) : D1 = DET * A
  T0 = T0 - (A1 * J0 + B1 * J1)
  T1 = T1 - (C1 * J0 + D1 * J1)
WEND
PRINT "y = ";T0;"+ (";T1;") * x"
END
