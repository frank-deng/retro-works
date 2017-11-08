DEFINT E-Z:DEFDBL A-D,R
COMMON SHARED A,B,C,D,R,GOAL,CANS
CANS=0

SUB CALC
    R=A+B+C+D:IF R=GOAL THEN PRINT A;"+";B;"+";C;"+";D;"=";R:GOTO FOUND
    R=A+B+C-D:IF R=GOAL THEN PRINT A;"+";B;"+";C;"-";D;"=";R:GOTO FOUND
    R=A+B-C-D:IF R=GOAL THEN PRINT A;"+";B;"-";C;"-";D;"=";R:GOTO FOUND
    R=A-B-C-D:IF R=GOAL THEN PRINT A;"-";B;"-";C;"-";D;"=";R:GOTO FOUND
    R=A*B*C*D:IF R=GOAL THEN PRINT A;"*";B;"*";C;"*";D;"=";R:GOTO FOUND
    R=A*B*C/D:IF R=GOAL THEN PRINT A;"*";B;"*";C;"/";D;"=";R:GOTO FOUND
    R=A*B/C/D:IF R=GOAL THEN PRINT A;"*";B;"/";C;"/";D;"=";R:GOTO FOUND
    R=A/B/C/D:IF R=GOAL THEN PRINT A;"/";B;"/";C;"/";D;"=";R:GOTO FOUND
    R=A+B+C*D:IF R=GOAL THEN PRINT A;"+";B;"+";C;"*";D;"=";R:GOTO FOUND
    R=(A+B+C)*D:IF R=GOAL THEN PRINT "(";A;"+";B;"+";C;")*";D;"=";R:GOTO FOUND
    R=A+(B+C)*D:IF R=GOAL THEN PRINT A;"+(";B;"+";C;")*";D;"=";R:GOTO FOUND
    R=(A+B)*(C+D):IF R=GOAL THEN PRINT "(";A;"+";B;")*(";C;"+";D;")=";R:GOTO FOUND
    R=A+B*C*D:IF R=GOAL THEN PRINT A;"+";B;"*";C;"*";D;"=";R:GOTO FOUND
    R=(A+B)*C*D:IF R=GOAL THEN PRINT "(";A;"+";B;")*";C;"*";D;"=";R:GOTO FOUND
    R=A*B+C*D:IF R=GOAL THEN PRINT A;"*";B;"+";C;"*";D;"=";R:GOTO FOUND
    R=(A+B*C)*D:IF R=GOAL THEN PRINT "(";A;"+";B;"*";C;")*";D;"=";R:GOTO FOUND
    R=A+B+C/D:IF R=GOAL THEN PRINT A;"+";B;"+";C;"/";D;"=";R:GOTO FOUND
    R=A+(B+C)/D:IF R=GOAL THEN PRINT A;"+(";B;"+";C;")/";D;"=";R:GOTO FOUND
    R=A+B/(C+D):IF R=GOAL THEN PRINT A;"+";B;"/(";C;"+";D;")=";R:GOTO FOUND
    R=(A+B+C)/D:IF R=GOAL THEN PRINT "(";A;"+";B;"+";C;")/";D;"=";R:GOTO FOUND
    R=A/(B+C+D):IF R=GOAL THEN PRINT A;"/(";B;"+";C;"+";D;")=";R:GOTO FOUND
    R=(A+B)/(C+D):IF R=GOAL THEN PRINT "(";A;"+";B;")/(";C;"+";D;")=";R:GOTO FOUND
    R=A+B/C/D:IF R=GOAL THEN PRINT A;"+";B;"/";C;"/";D;"=";R:GOTO FOUND
    R=(A+B)/C/D:IF R=GOAL THEN PRINT "(";A;"+";B;")/";C;"/";D;"=";R:GOTO FOUND
    R=A/(B+C)/D:IF R=GOAL THEN PRINT A;"/(";B;"+";C;")/";D;"=";R:GOTO FOUND
    R=A/B/(C+D):IF R=GOAL THEN PRINT A;"/";B;"/(";C;"+";D;")=";R:GOTO FOUND
    R=(A+B/C)/D:IF R=GOAL THEN PRINT "(";A;"+";B;"/";C;")/";D;"=";R:GOTO FOUND
    R=A/(B+C/D):IF R=GOAL THEN PRINT A;"/(";B;"+";C;"/";D;")=";R:GOTO FOUND
    R=A/B+C/D:IF R=GOAL THEN PRINT A;"/";B;"+";C;"/";D;"=";R:GOTO FOUND
    R=A-B-C*D:IF R=GOAL THEN PRINT A;"-";B;"-";C;"*";D;"=";R:GOTO FOUND
    R=A-B*C-D:IF R=GOAL THEN PRINT A;"-";B;"*";C;"-";D;"=";R:GOTO FOUND
    R=A*B-C-D:IF R=GOAL THEN PRINT A;"*";B;"-";C;"-";D;"=";R:GOTO FOUND
    R=A-(B-C)*D:IF R=GOAL THEN PRINT A;"-(";B;"-";C;")*";D;"=";R:GOTO FOUND
    R=(A-B)*C-D:IF R=GOAL THEN PRINT "(";A;"-";B;")*";C;"-";D;"=";R:GOTO FOUND
    R=(A-B-C)*D:IF R=GOAL THEN PRINT "(";A;"-";B;"-";C;")*";D;"=";R:GOTO FOUND
    R=(A-B)*(C-D):IF R=GOAL THEN PRINT "(";A;"-";B;")*(";C;"-";D;")=";R:GOTO FOUND
    R=A-B*C*D:IF R=GOAL THEN PRINT A;"-";B;"*";C;"*";D;"=";R:GOTO FOUND
    R=A*B*C-D:IF R=GOAL THEN PRINT A;"*";B;"*";C;"-";D;"=";R:GOTO FOUND
    R=(A-B)*C*D:IF R=GOAL THEN PRINT "(";A;"-";B;")*";C;"*";D;"=";R:GOTO FOUND
    R=(A-B*C)*D:IF R=GOAL THEN PRINT "(";A;"-";B;"*";C;")*";D;"=";R:GOTO FOUND
    R=(A*B-C)*D:IF R=GOAL THEN PRINT "(";A;"*";B;"-";C;")*";D;"=";R:GOTO FOUND
    R=A*B-C*D:IF R=GOAL THEN PRINT A;"*";B;"-";C;"*";D;"=";R:GOTO FOUND
    R=A-B-C/D:IF R=GOAL THEN PRINT A;"-";B;"-";C;"/";D;"=";R:GOTO FOUND
    R=A-B/C-D:IF R=GOAL THEN PRINT A;"-";B;"/";C;"-";D;"=";R:GOTO FOUND
    R=A/B-C-D:IF R=GOAL THEN PRINT A;"/";B;"-";C;"-";D;"=";R:GOTO FOUND
    R=A-(B-C)/D:IF R=GOAL THEN PRINT A;"-(";B;"-";C;")/";D;"=";R:GOTO FOUND
    R=A-B/(C-D):IF R=GOAL THEN PRINT A;"-";B;"/(";C;"-";D;")=";R:GOTO FOUND
    R=(A-B)/C-D:IF R=GOAL THEN PRINT "(";A;"-";B;")/";C;"-";D;"=";R:GOTO FOUND
    R=A/(B-C)-D:IF R=GOAL THEN PRINT A;"/(";B;"-";C;")-";D;"=";R:GOTO FOUND
    R=(A-B-C)/D:IF R=GOAL THEN PRINT "(";A;"-";B;"-";C;")/";D;"=";R:GOTO FOUND
    R=A/(B-C-D):IF R=GOAL THEN PRINT A;"/(";B;"-";C;"-";D;")=";R:GOTO FOUND
    R=(A-B)/(C-D):IF R=GOAL THEN PRINT "(";A;"-";B;")/(";C;"-";D;")=";R:GOTO FOUND
    R=A-B/C/D:IF R=GOAL THEN PRINT A;"-";B;"/";C;"/";D;"=";R:GOTO FOUND
    R=A/B/C-D:IF R=GOAL THEN PRINT A;"/";B;"/";C;"-";D;"=";R:GOTO FOUND
    R=A/B-C/D:IF R=GOAL THEN PRINT A;"/";B;"-";C;"/";D;"=";R:GOTO FOUND
    R=(A-B)/C/D:IF R=GOAL THEN PRINT "(";A;"-";B;")/";C;"/";D;"=";R:GOTO FOUND
    R=A/(B-C)/D:IF R=GOAL THEN PRINT A;"/(";B;"-";C;")/";D;"=";R:GOTO FOUND
    R=A/B/(C-D):IF R=GOAL THEN PRINT A;"/";B;"/(";C;"-";D;")=";R:GOTO FOUND
    R=(A-B/C)/D:IF R=GOAL THEN PRINT "(";A;"-";B;"/";C;")/";D;"=";R:GOTO FOUND
    R=(A/B-C)/D:IF R=GOAL THEN PRINT "(";A;"/";B;"-";C;")/";D;"=";R:GOTO FOUND
    R=A/(B-C/D):IF R=GOAL THEN PRINT A;"/(";B;"-";C;"/";D;")=";R:GOTO FOUND
    R=A/(B/C-D):IF R=GOAL THEN PRINT A;"/(";B;"/";C;"-";D;")=";R:GOTO FOUND
    R=A+B-C*D:IF R=GOAL THEN PRINT A;"+";B;"-";C;"*";D;"=";R:GOTO FOUND
    R=A+B*C-D:IF R=GOAL THEN PRINT A;"+";B;"*";C;"-";D;"=";R:GOTO FOUND
    R=A+(B-C)*D:IF R=GOAL THEN PRINT A;"+(";B;"-";C;")*";D;"=";R:GOTO FOUND
    R=A-(B+C)*D:IF R=GOAL THEN PRINT A;"-(";B;"+";C;")*";D;"=";R:GOTO FOUND
    R=(A+B)*C-D:IF R=GOAL THEN PRINT "(";A;"+";B;")*";C;"-";D;"=";R:GOTO FOUND
    R=(A+B-C)*D:IF R=GOAL THEN PRINT "(";A;"+";B;"-";C;")*";D;"=";R:GOTO FOUND
    R=(A+B)*(C-D):IF R=GOAL THEN PRINT "(";A;"+";B;")*(";C;"-";D;")=";R:GOTO FOUND
    R=A+B-C/D:IF R=GOAL THEN PRINT A;"+";B;"-";C;"/";D;"=";R:GOTO FOUND
    R=A+B/C-D:IF R=GOAL THEN PRINT A;"+";B;"/";C;"-";D;"=";R:GOTO FOUND
    R=A+(B-C)/D:IF R=GOAL THEN PRINT A;"+(";B;"-";C;")/";D;"=";R:GOTO FOUND
    R=A+B/(C-D):IF R=GOAL THEN PRINT A;"+";B;"/(";C;"-";D;")=";R:GOTO FOUND
    R=A-(B+C)/D:IF R=GOAL THEN PRINT A;"-(";B;"+";C;")/";D;"=";R:GOTO FOUND
    R=A-B/(C+D):IF R=GOAL THEN PRINT A;"-";B;"/(";C;"+";D;")=";R:GOTO FOUND
    R=(A+B)/C-D:IF R=GOAL THEN PRINT "(";A;"+";B;")/";C;"-";D;"=";R:GOTO FOUND
    R=A/(B+C)-D:IF R=GOAL THEN PRINT A;"/(";B;"+";C;")-";D;"=";R:GOTO FOUND
    R=(A+B-C)/D:IF R=GOAL THEN PRINT "(";A;"+";B;"-";C;")/";D;"=";R:GOTO FOUND
    R=A/(B+C-D):IF R=GOAL THEN PRINT A;"/(";B;"+";C;"-";D;")=";R:GOTO FOUND
    R=(A+B)/(C-D):IF R=GOAL THEN PRINT "(";A;"+";B;")/(";C;"-";D;")=";R:GOTO FOUND
    R=(A-B)/(C+D):IF R=GOAL THEN PRINT "(";A;"-";B;")/(";C;"+";D;")=";R:GOTO FOUND
    R=A+B*C/D:IF R=GOAL THEN PRINT A;"+";B;"*";C;"/";D;"=";R:GOTO FOUND
    R=(A+B)*C/D:IF R=GOAL THEN PRINT "(";A;"+";B;")*";C;"/";D;"=";R:GOTO FOUND
    R=A/(B+C)*D:IF R=GOAL THEN PRINT A;"/(";B;"+";C;")*";D;"=";R:GOTO FOUND
    R=A*B+C/D:IF R=GOAL THEN PRINT A;"*";B;"+";C;"/";D;"=";R:GOTO FOUND
    R=(A+B*C)/D:IF R=GOAL THEN PRINT "(";A;"+";B;"*";C;")/";D;"=";R:GOTO FOUND
    R=A/(B+C*D):IF R=GOAL THEN PRINT A;"/(";B;"+";C;"*";D;")=";R:GOTO FOUND
    R=(A+B/C)*D:IF R=GOAL THEN PRINT "(";A;"+";B;"/";C;")*";D;"=";R:GOTO FOUND
    R=A-B*C/D:IF R=GOAL THEN PRINT A;"-";B;"*";C;"/";D;"=";R:GOTO FOUND
    R=A*B/C-D:IF R=GOAL THEN PRINT A;"*";B;"/";C;"-";D;"=";R:GOTO FOUND
    R=(A-B)*C/D:IF R=GOAL THEN PRINT "(";A;"-";B;")*";C;"/";D;"=";R:GOTO FOUND
    R=A/(B-C)*D:IF R=GOAL THEN PRINT A;"/(";B;"-";C;")*";D;"=";R:GOTO FOUND
    R=A*B-C/D:IF R=GOAL THEN PRINT A;"*";B;"-";C;"/";D;"=";R:GOTO FOUND
    R=A/B-C*D:IF R=GOAL THEN PRINT A;"/";B;"-";C;"*";D;"=";R:GOTO FOUND
    R=(A-B*C)/D:IF R=GOAL THEN PRINT "(";A;"-";B;"*";C;")/";D;"=";R:GOTO FOUND
    R=A/(B-C*D):IF R=GOAL THEN PRINT A;"/(";B;"-";C;"*";D;")=";R:GOTO FOUND
    R=(A*B-C)/D:IF R=GOAL THEN PRINT "(";A;"*";B;"-";C;")/";D;"=";R:GOTO FOUND
    R=A/(B*C-D):IF R=GOAL THEN PRINT A;"/(";B;"*";C;"-";D;")=";R:GOTO FOUND
    R=(A-B/C)*D:IF R=GOAL THEN PRINT "(";A;"-";B;"/";C;")*";D;"=";R:GOTO FOUND
    GOTO CALCFINISH
    FOUND:
    CANS=1
    CALCFINISH:
END SUB

SUB MAIN
    DIM N(4)
    INPUT "A,B,C,D,Goal:",N(0),N(1),N(2),N(3),GOAL
    FOR I=0 TO 3
        FOR J=0 TO 3
           IF I=J THEN GOTO SKIPJ
           FOR K=0 TO 3
               IF I<>K AND J<>K THEN
                   A=N(I):B=N(J):C=N(K):D=N(6-I-J-K)
                   CALC
                   IF CANS > 0 THEN GOTO FINISH
               END IF
           NEXT K
SKIPJ:
        NEXT J
    NEXT I
    PRINT "No Answer."
FINISH:
END SUB
MAIN