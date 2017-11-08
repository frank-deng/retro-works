DEFINT A-Z

FUNCTION COMP(M,N)
    STATIC I,J,A,B
    A = 0 : B = 0
    FOR I = 0 TO 3 STEP 1
        IF (M\(10^I) MOD 10) = (N\(10^I) MOD 10) THEN
            A = A+1
        ELSE
            FOR J = 0 TO 3 STEP 1
                IF (I<>J) AND ((M\(10^I) MOD 10) = (N\(10^J) MOD 10)) THEN
                    B = B+1
                END IF
            NEXT J
        END IF
    NEXT I
    COMP = A * 10 + B
END FUNCTION

FUNCTION CHECK(N)
    STATIC I,J,F
    IF N<123 OR N>9876 THEN
        F = 0 : GOTO CHECKFINISHED
    END IF
    F = 1
    FOR I = 0 TO 2 STEP 1
        FOR J = I+1 TO 3 STEP 1
            IF (N\(10^I) MOD 10) = (N\(10^J) MOD 10) THEN
                F = 0 : GOTO CHECKFINISHED
            END IF
        NEXT J
    NEXT I
CHECKFINISHED:
    CHECK = F
END FUNCTION

DIM SHARED GSTATE(8,2)
COMMON SHARED GSTATELEN

SUB INPUTGSTATE
    GSTATELEN = 0 : I = 1
    WHILE GSTATELEN < 8 AND I
        INPUT "Guess,A,B:",G,A,B
        IF G=0 THEN
            I = 0
        ELSEIF CHECK(G)=0 OR A<0 OR A>3 OR B<0 OR B>4 OR A+B>4 THEN
            PRINT "Invalid Input!"
        ELSE
            GSTATE(GSTATELEN,0)=G
            GSTATE(GSTATELEN,1)=A*10+B
            GSTATELEN = GSTATELEN+1
        END IF
    WEND
END SUB

SUB SHOWRESULT
    PRINT ""
    FOR N = 123 TO 9876 STEP 1
        IF INKEY$ <> "" THEN GOTO FINISH
        IF CHECK(N)=1 THEN
            FOR I = 0 TO GSTATELEN-1 STEP 1
                IF COMP(N,GSTATE(I,0)) <> GSTATE(I,1) THEN GOTO NOTPASSED
            NEXT I
            PRINT USING "#####";N;
NOTPASSED:
        END IF
    NEXT N
FINISH:
    PRINT ""
END SUB

SUB MAIN
    INPUTGSTATE
    IF GSTATELEN > 0 THEN
        SHOWRESULT
    END IF
END SUB
MAIN

