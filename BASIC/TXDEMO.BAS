DECLARE SUB TestTX ()
DECLARE FUNCTION n$ (n%)
DECLARE SUB TX (s AS STRING)
DATA &H50,&H53,&H56,&HBE,&H0,&H0,&H2E,&HC7,&H4,&H0,&H0,&HB8,&H0,&HDB,&HCD,&H2F,&H3C,&HFF,&H75,&H12,&H81,&HFB,&H50,&H54,&H75,&HC,&HB8,&H11,&H0,&HCD,&H79,&H75,&H5,&H2E,&HC7,&H4,&H1,&H0,&H5E,&H5B,&H58,&HCB

DEFINT A-Z
TestTX
OPEN "LPT3" FOR OUTPUT AS #1
TX ("M10CU1,0CO8KB1,0CL0")

I = 0
FOR y = 0 TO 15
  FOR x = 0 TO 15
    TX ("CO" + n$(I) + "B" + n$(x * 40) + "," + n$(y * 30) + "," + n$(x * 40 + 40) + "," + n$(y * 30 + 30))
    I = I + 1
  NEXT x
NEXT y
WHILE INPUT$(1) = "": WEND

TX ("CL0CO0B0,0,640,480CO7")
I = 0
FOR y = 0 TO 8
  FOR x = 0 TO 3
    TX ("{(7@52,52=" + n$(I) + "-" + n$(x * 160) + "|" + n$(y * 53) + "}")
    TX ("{×ÖÌå" + n$(I) + "}")
    I = I + 1
  NEXT x
NEXT y
WHILE INPUT$(1) = "": WEND

TX ("KB1,1M3CU1,1")
CLOSE
END

FUNCTION n$ (A AS INTEGER)
n$ = LTRIM$(RTRIM$(STR$(A)))
END FUNCTION

SUB TestTX
DIM A%(50)
DEF SEG = VARSEG(A%(0))
RESTORE
FOR I% = 0 TO 41
    READ D%
    IF I% = 4 THEN
       D% = VARPTR(A%(49)) MOD 256
    ELSEIF I% = 5 THEN
       D% = VARPTR(A%(49)) / 256
    END IF
    POKE VARPTR(A%(0)) + I%, D%
NEXT I%
CALL ABSOLUTE(VARPTR(A%(0)))
DEF SEG
IF A%(49) = 0 THEN
   PRINT "Please run TX.COM first"
   END
END IF
END SUB

SUB TX (s AS STRING)
PRINT #1, CHR$(14); "["; s; "]";
END SUB
