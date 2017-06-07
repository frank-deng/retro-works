DEFINT A-Z: DEFSTR C: C = CHR$(14): OPEN "LPT3" FOR OUTPUT AS #1
PRINT #1, C; "[M10CU1,0CL]"
X = 0: Y = 0
FOR I = 0 TO 33
  PRINT #1, C; "[{-"; LTRIM$(STR$(X)); "|"; LTRIM$(STR$(Y)); "="; LTRIM$(STR$(I)); "&0^0@42,42}{×ÖÌå"; LTRIM$(STR$(I)); "}]";
  X = X + 42 * 4
  IF X > 640 - 42 * 3 THEN
    X = 0: Y = Y + 42
  END IF
NEXT I
WHILE INPUT$(1) = "": WEND
PRINT #1, C; "[SA0,0,640,480,D:\FONTS.PCX]"
PRINT #1, C; "[M3CU1,1]"
CLOSE
END

