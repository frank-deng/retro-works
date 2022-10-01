DECLARE FUNCTION CNUM1E8% (S$)
DECLARE FUNCTION CNUM10000% (S$)
DECLARE FUNCTION CNUM1000% (S$)
DEFINT A-Z: DIM SHARED N$(15): FOR I = 0 TO 14: READ N$(I): NEXT I
DATA "Áã","Ò¼","·¡","Èþ","ËÁ","Îé","Â½","Æâ","°Æ","¾Á","Ê°","°Û","Çª","Íò","ÒÚ"
INPUT "Input Number: ", IN$
IF LEN(IN$) > 16 THEN PRINT "Input too long.": END
R = CNUM1E8%(IN$)
PRINT ""
END

FUNCTION CNUM1000 (S$)
    IF VAL(S$) = 0 THEN
        CNUM1000 = 0
        EXIT FUNCTION
    END IF
    OUTZERO = 0
    L = LEN(S$)
    FOR I = L TO 1 STEP -1
        DIGIT = VAL(MID$(S$, L + 1 - I, 1))
        IF DIGIT <> 0 THEN
            IF OUTZERO <> 0 THEN PRINT N$(0); : OUTZERO = 0
            PRINT N$(DIGIT);
            SELECT CASE I
                CASE 2
                    PRINT N$(10);
                CASE 3
                    PRINT N$(11);
                CASE 4
                    PRINT N$(12);
            END SELECT
        ELSE
           OUTZERO = 1
        END IF
    NEXT I
    CNUM1000% = 1
END FUNCTION

FUNCTION CNUM10000% (S$)
    L = LEN(S$)
    IF L <= 4 THEN
        CNUM10000% = CNUM1000%(S$)
        EXIT FUNCTION
    END IF
    A1 = CNUM1000%(MID$(S$, 1, L - 4))
    IF A1 <> 0 THEN PRINT N$(13);
    A2 = CNUM1000%(MID$(S$, L - 4 + 1, 4))
    CNUM10000% = A1 OR A2
END FUNCTION

FUNCTION CNUM1E8% (S$)
    L = LEN(S$)
    IF L <= 8 THEN
        CNUM1E8% = CNUM10000%(S$)
        EXIT FUNCTION
    END IF
    A1 = CNUM10000%(MID$(S$, 1, L - 8))
    IF A1 <> 0 THEN PRINT N$(14);
    A2 = CNUM10000%(MID$(S$, L - 8 + 1, 8))
    CNUM1E8% = A1 OR A2
END FUNCTION

