DATA &H50,&H53,&H56,&HBE,&H00,&H00,&H2E,&HC7,&H04,&H00,&H00,&HB8,&H00,&HDB,&HCD,&H2F
DATA &H3C,&HFF,&H75,&H12,&H81,&HFB,&H50,&H54,&H75,&H0C,&HB8,&H11,&H00,&HCD,&H79,&H75
DATA &H05,&h2E,&HC7,&H04,&H01,&H00,&H5E,&H5B,&H58,&HCB
SUB TestTx
DIM a%(50)
DEF SEG = VARSEG(a%(0))
RESTORE
FOR I% = 0 TO 41
    READ D%
    IF I% = 4 THEN
       D% = VARPTR(a%(49)) MOD 256
    ELSEIF I% = 5 THEN
       D% = VARPTR(a%(49)) / 256
    END IF
    POKE VARPTR(a%(0)) + I%, D%
NEXT I%
CALL ABSOLUTE(VARPTR(a%(0)))
DEF SEG
IF a%(49) = 0 THEN
   PRINT "Please run TX.COM first"
   END
END IF
END SUB

FUNCTION num2str(n)
num2str=LTRIM$(RTRIM$(STR$(n)))
END FUNCTION

SUB TX(s as string)
PRINT #1, CHR$(14);"[";s;"]";
END SUB

' -------- '

TestTx
OPEN "LPT3" FOR OUTPUT AS #1
PRINT #1, CHR$(14); "[M18CU1,0]"

X$=num2str(12);
Y$=num2str(16);
TX("")

PRINT #1, CHR$(14); "[M3CU1,1]"
CLOSE
END
