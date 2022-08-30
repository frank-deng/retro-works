10 DEFDBL A-Z : DEFINT I,L: DIM X(2048), Y(2048)
20 PRINT "*** Linear Regression Demo ***": PRINT ""
21 PRINT "Hint: Input a single comma to end."
30 WHILE 1: INPUT "X,Y: ", X$, Y$
40 IF X$="" OR Y$="" THEN GOTO 90
50 X(L)=VAL(X$): Y(L)=VAL(Y$): L=L+1
60 WEND
90 T0 = 0 : T1 = 0 : J0 = 1 : J1 = 1
100 WHILE ABS(J0)>0.0001 OR ABS(J1)>0.0001
110 A = 1 : B = 0 : D = 0 : J0 = 0 : J1 = 0
120 FOR I = 0 TO L-1
130 B = B + X(I)
140 D = D + X(I) * X(I)
150 H = T0 + T1 * X(I)
160 J0 = J0 + (H - Y(I))
170 J1 = J1 + (H - Y(I)) * X(I)
180 NEXT I
190 B = B / L : C = B : D = D / L
200 J0 = J0 / L : J1 = J1 / L
210 DET = 1 / (A*D-B*C)
220 A1 = DET * D : B1 = DET * (-B)
230 C1 = DET * (-C) : D1 = DET * A
240 T0 = T0 - (A1 * J0 + B1 * J1)
250 T1 = T1 - (C1 * J0 + D1 * J1)
260 WEND
270 PRINT "": PRINT "y = ";T0;"+ (";T1;") * x": PRINT ""
280 END

