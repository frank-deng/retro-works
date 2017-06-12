DECLARE SUB TXRect (x0%, y0%, x1%, y1%, fill%)
DECLARE SUB TXColor (col%)
DECLARE SUB TXTextAttr (font%, w%, h%, fg%, bg%, sp%)
DECLARE SUB TXText (text$, x%, y%)
DECLARE SUB TXInit ()
DECLARE SUB TXQuit ()
CALL TXInit
CALL TXColor(1)
CALL TXRect(0, 0, 640, 480, 1)
CALL TXTextAttr(8, 64, 64, 14, -1, 0)
CALL TXText("天生我材必有用，", (640 - 16 * 32) / 2, 240 - 64)
CALL TXText("千金散尽还复来。", (640 - 16 * 32) / 2, 240)
WHILE INPUT$(1) = "": WEND
CALL TXQuit
END

