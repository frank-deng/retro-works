10 DEFINT A-Z: DEFDBL P, T: W = 128: H = 75: OY = 65: F = 56.7
20 KEY OFF: SCREEN 1: COLOR 0, 2: CLS : PI = 3.141592654#
30 LINE (160, 0)-(160, 199), 1, , &H3333
40 LINE (0, OY)-(319, OY), 1, , &H3333
50 Y0 = OY: FOR X = -W TO W
60 X# = X * PI / (2 * W)
70 Y# = (.64 * SQR(ABS(X#)) - .8 + 1.2 ^ ABS(X#) * SIN(F * X#)) * SQR(ABS(COS(X#)))
80 Y = OY - INT(Y# * H + .5)
90 LINE (X + 159, Y0)-(X + 160, Y), 2: Y0 = Y
100 NEXT X
120 WHILE INPUT$(1) = "": WEND
130 SCREEN 0: WIDTH 80: CLS : END

