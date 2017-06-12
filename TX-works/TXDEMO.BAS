DECLARE SUB TXExec (cmd$)
DECLARE SUB TXColor (col%)
DECLARE SUB TXRect (x0%, y0%, x1%, y1%, fill%)
DECLARE SUB TXText (text$, X%, Y%)
DECLARE SUB TXTextAttr (font%, W%, H%, fg%, bg%, sp%)
DECLARE SUB TXInit ()
DECLARE SUB TXQuit ()
DEFINT A-Z
CALL TXInit
CALL TXColor(0)
CALL TXRect(0, 0, 640, 480, 1)
X = 0: Y = 0: size = 50
FOR I = 0 TO 33
  CALL TXTextAttr(I, size, size, 7, 0, 0)
  CALL TXText("×ÖÌå" + LTRIM$(STR$(I)), X, Y)
  X = X + size * 3 + 10
  IF X > 640 - size * 3 THEN
    X = 0: Y = Y + size
  END IF
NEXT I
WHILE INPUT$(1) = "": WEND
TXExec ("CL")
W = 640 / 16: H = 480 / 16
FOR Y = 0 TO 15
  FOR X = 0 TO 15
    CALL TXColor(Y * 16 + X)
    CALL TXRect(X * W, Y * H, X * W + W, Y * H + H, 1)
  NEXT X
NEXT Y
WHILE INPUT$(1) = "": WEND
CALL TXQuit
END

