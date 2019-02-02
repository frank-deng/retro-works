DECLARE SUB TestTX ()
DECLARE FUNCTION n$ (n%)
DECLARE SUB TX (s AS STRING)
DECLARE SUB DrawText(x as integer,y as integer,text as string)
DATA &H50,&H53,&H56,&HBE,&H00,&H00,&H2E,&HC7,&H04,&H00,&H00,&HB8,&H00,&HDB,&HCD,&H2F
DATA &H3C,&HFF,&H75,&H12,&H81,&HFB,&H50,&H54,&H75,&H0C,&HB8,&H11,&H00,&HCD,&H79,&H75
DATA &H05,&h2E,&HC7,&H04,&H01,&H00,&H5E,&H5B,&H58,&HCB

DEFINT A-Z
TestTX
OPEN "LPT3" FOR OUTPUT AS #1
TX ("M18CU1,0KB1,0CL0CO4B0,0,640,480")
CALL BORDER(5)
CALL BORDER(6)
CALL BORDER(7)
CALL BORDER(10)

T$ = "»¶¶ÈÐÂÄê": L = LEN(T$)
SIZE = 120: X = (640 - SIZE * L / 2) / 2 : Y=240-SIZE
TX ("{=0%1@" + n$(SIZE) + "," + n$(SIZE) + "}")
TX ("{(15}"): CALL DrawText(X-1,Y-1,T$)
TX ("{(0}"): CALL DrawText(X+1,Y+1,T$)
TX ("{(14}"): CALL DrawText(X,Y,T$)

T$ = "Happy New Year": L = LEN(T$)
SIZE = 80: X = (640 - SIZE * L / 2) / 2 : Y=280
TX ("{=0%1@" + n$(SIZE) + "," + n$(SIZE) + "}")
TX ("{(15}"): CALL DrawText(X-1,Y-1,T$)
TX ("{(0}"): CALL DrawText(X+1,Y+1,T$)
TX ("{(14}"): CALL DrawText(X,Y,T$)

PLAY "MBT150O3 C8C8L4C<G> E8E8L4EC C8E8L4GG F8E8D2"
PLAY "MBD8E8L4FF E8D8L4EC C8E8L4D<G B8>D8C2P4"
PLAY "MBC8C8L4C<G> E8E8L4EC C8E8L4GG F8E8D2"
PLAY "MBD8E8L4FF E8D8L4EC C8E8L4D<G B8>D8C2"

WHILE INPUT$(1) = "": WEND
TX ("KB1,1M3CU1,1")
CLOSE
END

FUNCTION n$ (A AS INTEGER)
n$ = LTRIM$(RTRIM$(STR$(A)))
END FUNCTION

SUB BORDER(PAD AS INTEGER)
	TX("CO14R"+n$(PAD)+","+n$(PAD)+","+n$(639-PAD)+","+n$(479-PAD))
END SUB

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

SUB DrawText(x as integer,y as integer,text as string)
  TX ("{-" + n$(x) + "|" + n$(y) + CHR$(0) + text+"}")
END SUB
