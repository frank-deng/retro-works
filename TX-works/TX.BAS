
SUB TXColor (col%)
  PRINT #1, CHR$(14); "[CO"; col%; "]";
END SUB

SUB TXCopyScr (x0%, y0%, x1%, y1%, x2%, y2%)
  PRINT #1, CHR$(14); "[MI"; x0%; ","; y0%; ","; x1%; ","; y1%; ","; x2%; ","; y2%; "]";
END SUB

SUB TXExec (cmd$)
  PRINT #1, CHR$(14); "["; cmd$; "]";
END SUB

SUB TXInit
  OPEN "LPT3" FOR OUTPUT AS #1
  PRINT #1, CHR$(14); "[M10CU1,0CL{^0&0%1}]";
END SUB

SUB TXLoadPCX (x%, y%, pcx$)
  PRINT #1, CHR$(14); "[RE"; x%; ","; y%; ","; pcx$; "]";
END SUB

SUB TXQuit
  PRINT #1, CHR$(14); "[M3CU1,1KB1,1]";
  CLOSE #1
  CLS
END SUB

SUB TXRect (x0%, y0%, x1%, y1%, fill%)
  IF fill% > 0 THEN
    PRINT #1, CHR$(14); "[B"; x0%; ","; y0%; ","; x1%; ","; y1%; "]";
  ELSE
    PRINT #1, CHR$(14); "[R"; x0%; ","; y0%; ","; x1%; ","; y1%; "]";
  END IF
END SUB

SUB TXSavePCX (x0%, y0%, x1%, y1%, pcx$)
  PRINT #1, CHR$(14); "[SA"; x0%; ","; y0%; ","; x1%; ","; y1%; ","; pcx$; "]";
END SUB

SUB TXText (text$, x%, y%)
  PRINT #1, CHR$(14); "[{-"; LTRIM$(STR$(x%)); "|"; LTRIM$(STR$(y%)); text$; "}]";
END SUB

SUB TXTextAttr (font%, w%, h%, fg%, bg%, sp%)
  STATIC bg$
  IF bg% < 0 THEN
    bg$ = "%1"
  ELSE
    bg$ = ")" + LTRIM$(STR$(bg%))
  END IF
  PRINT #1, CHR$(14); "[{="; LTRIM$(STR$(font%)); "@"; LTRIM$(STR$(w%)); ","; LTRIM$(STR$(h%)); "^"; LTRIM$(STR$(sp%)); "("; LTRIM$(STR$(fg%)); bg$; "}]";
END SUB

