DEFINT E-Z:DEFDBL A-D,R
COMMON SHARED A,B,C,D,R,GOAL,FOUND

SUB CALC
    R=A+B+C+D:IF R=GOAL THEN PRINT A;"+";B;"+";C;"+";D;"=";R:GOTO LFOUND
    R=A+B+C-D:IF R=GOAL THEN PRINT A;"+";B;"+";C;"-";D;"=";R:GOTO LFOUND
    R=A+B-C-D:IF R=GOAL THEN PRINT A;"+";B;"-";C;"-";D;"=";R:GOTO LFOUND
    R=A-B-C-D:IF R=GOAL THEN PRINT A;"-";B;"-";C;"-";D;"=";R:GOTO LFOUND
    R=A*B*C*D:IF R=GOAL THEN PRINT A;"*";B;"*";C;"*";D;"=";R:GOTO LFOUND
    R=A*B*C/D:IF R=GOAL THEN PRINT A;"*";B;"*";C;"/";D;"=";R:GOTO LFOUND
    R=A*B/C/D:IF R=GOAL THEN PRINT A;"*";B;"/";C;"/";D;"=";R:GOTO LFOUND
    R=A/B/C/D:IF R=GOAL THEN PRINT A;"/";B;"/";C;"/";D;"=";R:GOTO LFOUND
    R=A+B+C*D:IF R=GOAL THEN PRINT A;"+";B;"+";C;"*";D;"=";R:GOTO LFOUND
    R=(A+B+C)*D:IF R=GOAL THEN PRINT "(";A;"+";B;"+";C;")*";D;"=";R:GOTO LFOUND
    R=A+(B+C)*D:IF R=GOAL THEN PRINT A;"+(";B;"+";C;")*";D;"=";R:GOTO LFOUND
    R=(A+B)*(C+D):IF R=GOAL THEN PRINT "(";A;"+";B;")*(";C;"+";D;")=";R:GOTO LFOUND
    R=A+B*C*D:IF R=GOAL THEN PRINT A;"+";B;"*";C;"*";D;"=";R:GOTO LFOUND
    R=(A+B)*C*D:IF R=GOAL THEN PRINT "(";A;"+";B;")*";C;"*";D;"=";R:GOTO LFOUND
    R=A*B+C*D:IF R=GOAL THEN PRINT A;"*";B;"+";C;"*";D;"=";R:GOTO LFOUND
    R=(A+B*C)*D:IF R=GOAL THEN PRINT "(";A;"+";B;"*";C;")*";D;"=";R:GOTO LFOUND
    R=A+B+C/D:IF R=GOAL THEN PRINT A;"+";B;"+";C;"/";D;"=";R:GOTO LFOUND
    R=A+(B+C)/D:IF R=GOAL THEN PRINT A;"+(";B;"+";C;")/";D;"=";R:GOTO LFOUND
    R=A+B/(C+D):IF R=GOAL THEN PRINT A;"+";B;"/(";C;"+";D;")=";R:GOTO LFOUND
    R=(A+B+C)/D:IF R=GOAL THEN PRINT "(";A;"+";B;"+";C;")/";D;"=";R:GOTO LFOUND
    R=A/(B+C+D):IF R=GOAL THEN PRINT A;"/(";B;"+";C;"+";D;")=";R:GOTO LFOUND
    R=(A+B)/(C+D):IF R=GOAL THEN PRINT "(";A;"+";B;")/(";C;"+";D;")=";R:GOTO LFOUND
    R=A+B/C/D:IF R=GOAL THEN PRINT A;"+";B;"/";C;"/";D;"=";R:GOTO LFOUND
    R=(A+B)/C/D:IF R=GOAL THEN PRINT "(";A;"+";B;")/";C;"/";D;"=";R:GOTO LFOUND
    R=A/(B+C)/D:IF R=GOAL THEN PRINT A;"/(";B;"+";C;")/";D;"=";R:GOTO LFOUND
    R=A/B/(C+D):IF R=GOAL THEN PRINT A;"/";B;"/(";C;"+";D;")=";R:GOTO LFOUND
    R=(A+B/C)/D:IF R=GOAL THEN PRINT "(";A;"+";B;"/";C;")/";D;"=";R:GOTO LFOUND
    R=A/(B+C/D):IF R=GOAL THEN PRINT A;"/(";B;"+";C;"/";D;")=";R:GOTO LFOUND
    R=A/B+C/D:IF R=GOAL THEN PRINT A;"/";B;"+";C;"/";D;"=";R:GOTO LFOUND
    R=A-B-C*D:IF R=GOAL THEN PRINT A;"-";B;"-";C;"*";D;"=";R:GOTO LFOUND
    R=A-B*C-D:IF R=GOAL THEN PRINT A;"-";B;"*";C;"-";D;"=";R:GOTO LFOUND
    R=A*B-C-D:IF R=GOAL THEN PRINT A;"*";B;"-";C;"-";D;"=";R:GOTO LFOUND
    R=A-(B-C)*D:IF R=GOAL THEN PRINT A;"-(";B;"-";C;")*";D;"=";R:GOTO LFOUND
    R=(A-B)*C-D:IF R=GOAL THEN PRINT "(";A;"-";B;")*";C;"-";D;"=";R:GOTO LFOUND
    R=(A-B-C)*D:IF R=GOAL THEN PRINT "(";A;"-";B;"-";C;")*";D;"=";R:GOTO LFOUND
    R=(A-B)*(C-D):IF R=GOAL THEN PRINT "(";A;"-";B;")*(";C;"-";D;")=";R:GOTO LFOUND
    R=A-B*C*D:IF R=GOAL THEN PRINT A;"-";B;"*";C;"*";D;"=";R:GOTO LFOUND
    R=A*B*C-D:IF R=GOAL THEN PRINT A;"*";B;"*";C;"-";D;"=";R:GOTO LFOUND
    R=(A-B)*C*D:IF R=GOAL THEN PRINT "(";A;"-";B;")*";C;"*";D;"=";R:GOTO LFOUND
    R=(A-B*C)*D:IF R=GOAL THEN PRINT "(";A;"-";B;"*";C;")*";D;"=";R:GOTO LFOUND
    R=(A*B-C)*D:IF R=GOAL THEN PRINT "(";A;"*";B;"-";C;")*";D;"=";R:GOTO LFOUND
    R=A*B-C*D:IF R=GOAL THEN PRINT A;"*";B;"-";C;"*";D;"=";R:GOTO LFOUND
    R=A-B-C/D:IF R=GOAL THEN PRINT A;"-";B;"-";C;"/";D;"=";R:GOTO LFOUND
    R=A-B/C-D:IF R=GOAL THEN PRINT A;"-";B;"/";C;"-";D;"=";R:GOTO LFOUND
    R=A/B-C-D:IF R=GOAL THEN PRINT A;"/";B;"-";C;"-";D;"=";R:GOTO LFOUND
    R=A-(B-C)/D:IF R=GOAL THEN PRINT A;"-(";B;"-";C;")/";D;"=";R:GOTO LFOUND
    R=A-B/(C-D):IF R=GOAL THEN PRINT A;"-";B;"/(";C;"-";D;")=";R:GOTO LFOUND
    R=(A-B)/C-D:IF R=GOAL THEN PRINT "(";A;"-";B;")/";C;"-";D;"=";R:GOTO LFOUND
    R=A/(B-C)-D:IF R=GOAL THEN PRINT A;"/(";B;"-";C;")-";D;"=";R:GOTO LFOUND
    R=(A-B-C)/D:IF R=GOAL THEN PRINT "(";A;"-";B;"-";C;")/";D;"=";R:GOTO LFOUND
    R=A/(B-C-D):IF R=GOAL THEN PRINT A;"/(";B;"-";C;"-";D;")=";R:GOTO LFOUND
    R=(A-B)/(C-D):IF R=GOAL THEN PRINT "(";A;"-";B;")/(";C;"-";D;")=";R:GOTO LFOUND
    R=A-B/C/D:IF R=GOAL THEN PRINT A;"-";B;"/";C;"/";D;"=";R:GOTO LFOUND
    R=A/B/C-D:IF R=GOAL THEN PRINT A;"/";B;"/";C;"-";D;"=";R:GOTO LFOUND
    R=A/B-C/D:IF R=GOAL THEN PRINT A;"/";B;"-";C;"/";D;"=";R:GOTO LFOUND
    R=(A-B)/C/D:IF R=GOAL THEN PRINT "(";A;"-";B;")/";C;"/";D;"=";R:GOTO LFOUND
    R=A/(B-C)/D:IF R=GOAL THEN PRINT A;"/(";B;"-";C;")/";D;"=";R:GOTO LFOUND
    R=A/B/(C-D):IF R=GOAL THEN PRINT A;"/";B;"/(";C;"-";D;")=";R:GOTO LFOUND
    R=(A-B/C)/D:IF R=GOAL THEN PRINT "(";A;"-";B;"/";C;")/";D;"=";R:GOTO LFOUND
    R=(A/B-C)/D:IF R=GOAL THEN PRINT "(";A;"/";B;"-";C;")/";D;"=";R:GOTO LFOUND
    R=A/(B-C/D):IF R=GOAL THEN PRINT A;"/(";B;"-";C;"/";D;")=";R:GOTO LFOUND
    R=A/(B/C-D):IF R=GOAL THEN PRINT A;"/(";B;"/";C;"-";D;")=";R:GOTO LFOUND
    R=A+B-C*D:IF R=GOAL THEN PRINT A;"+";B;"-";C;"*";D;"=";R:GOTO LFOUND
    R=A+B*C-D:IF R=GOAL THEN PRINT A;"+";B;"*";C;"-";D;"=";R:GOTO LFOUND
    R=A+(B-C)*D:IF R=GOAL THEN PRINT A;"+(";B;"-";C;")*";D;"=";R:GOTO LFOUND
    R=A-(B+C)*D:IF R=GOAL THEN PRINT A;"-(";B;"+";C;")*";D;"=";R:GOTO LFOUND
    R=(A+B)*C-D:IF R=GOAL THEN PRINT "(";A;"+";B;")*";C;"-";D;"=";R:GOTO LFOUND
    R=(A+B-C)*D:IF R=GOAL THEN PRINT "(";A;"+";B;"-";C;")*";D;"=";R:GOTO LFOUND
    R=(A+B)*(C-D):IF R=GOAL THEN PRINT "(";A;"+";B;")*(";C;"-";D;")=";R:GOTO LFOUND
    R=A+B-C/D:IF R=GOAL THEN PRINT A;"+";B;"-";C;"/";D;"=";R:GOTO LFOUND
    R=A+B/C-D:IF R=GOAL THEN PRINT A;"+";B;"/";C;"-";D;"=";R:GOTO LFOUND
    R=A+(B-C)/D:IF R=GOAL THEN PRINT A;"+(";B;"-";C;")/";D;"=";R:GOTO LFOUND
    R=A+B/(C-D):IF R=GOAL THEN PRINT A;"+";B;"/(";C;"-";D;")=";R:GOTO LFOUND
    R=A-(B+C)/D:IF R=GOAL THEN PRINT A;"-(";B;"+";C;")/";D;"=";R:GOTO LFOUND
    R=A-B/(C+D):IF R=GOAL THEN PRINT A;"-";B;"/(";C;"+";D;")=";R:GOTO LFOUND
    R=(A+B)/C-D:IF R=GOAL THEN PRINT "(";A;"+";B;")/";C;"-";D;"=";R:GOTO LFOUND
    R=A/(B+C)-D:IF R=GOAL THEN PRINT A;"/(";B;"+";C;")-";D;"=";R:GOTO LFOUND
    R=(A+B-C)/D:IF R=GOAL THEN PRINT "(";A;"+";B;"-";C;")/";D;"=";R:GOTO LFOUND
    R=A/(B+C-D):IF R=GOAL THEN PRINT A;"/(";B;"+";C;"-";D;")=";R:GOTO LFOUND
    R=(A+B)/(C-D):IF R=GOAL THEN PRINT "(";A;"+";B;")/(";C;"-";D;")=";R:GOTO LFOUND
    R=(A-B)/(C+D):IF R=GOAL THEN PRINT "(";A;"-";B;")/(";C;"+";D;")=";R:GOTO LFOUND
    R=A+B*C/D:IF R=GOAL THEN PRINT A;"+";B;"*";C;"/";D;"=";R:GOTO LFOUND
    R=(A+B)*C/D:IF R=GOAL THEN PRINT "(";A;"+";B;")*";C;"/";D;"=";R:GOTO LFOUND
    R=A/(B+C)*D:IF R=GOAL THEN PRINT A;"/(";B;"+";C;")*";D;"=";R:GOTO LFOUND
    R=A*B+C/D:IF R=GOAL THEN PRINT A;"*";B;"+";C;"/";D;"=";R:GOTO LFOUND
    R=(A+B*C)/D:IF R=GOAL THEN PRINT "(";A;"+";B;"*";C;")/";D;"=";R:GOTO LFOUND
    R=A/(B+C*D):IF R=GOAL THEN PRINT A;"/(";B;"+";C;"*";D;")=";R:GOTO LFOUND
    R=(A+B/C)*D:IF R=GOAL THEN PRINT "(";A;"+";B;"/";C;")*";D;"=";R:GOTO LFOUND
    R=A-B*C/D:IF R=GOAL THEN PRINT A;"-";B;"*";C;"/";D;"=";R:GOTO LFOUND
    R=A*B/C-D:IF R=GOAL THEN PRINT A;"*";B;"/";C;"-";D;"=";R:GOTO LFOUND
    R=(A-B)*C/D:IF R=GOAL THEN PRINT "(";A;"-";B;")*";C;"/";D;"=";R:GOTO LFOUND
    R=A/(B-C)*D:IF R=GOAL THEN PRINT A;"/(";B;"-";C;")*";D;"=";R:GOTO LFOUND
    R=A*B-C/D:IF R=GOAL THEN PRINT A;"*";B;"-";C;"/";D;"=";R:GOTO LFOUND
    R=A/B-C*D:IF R=GOAL THEN PRINT A;"/";B;"-";C;"*";D;"=";R:GOTO LFOUND
    R=(A-B*C)/D:IF R=GOAL THEN PRINT "(";A;"-";B;"*";C;")/";D;"=";R:GOTO LFOUND
    R=A/(B-C*D):IF R=GOAL THEN PRINT A;"/(";B;"-";C;"*";D;")=";R:GOTO LFOUND
    R=(A*B-C)/D:IF R=GOAL THEN PRINT "(";A;"*";B;"-";C;")/";D;"=";R:GOTO LFOUND
    R=A/(B*C-D):IF R=GOAL THEN PRINT A;"/(";B;"*";C;"-";D;")=";R:GOTO LFOUND
    R=(A-B/C)*D:IF R=GOAL THEN PRINT "(";A;"-";B;"/";C;")*";D;"=";R:GOTO LFOUND
    EXIT SUB
LFOUND:
    FOUND=1 : EXIT SUB
END SUB

SUB MAIN
    DIM N(4) : FOUND=0
    INPUT "A,B,C,D,Goal:",N(0),N(1),N(2),N(3),GOAL
    FOR I=0 TO 3
    FOR J=0 TO 3
      IF I<>J THEN
      FOR K=0 TO 3
        IF I<>K AND J<>K THEN
          A=N(I):B=N(J):C=N(K):D=N(6-I-J-K)
          CALC
          IF FOUND > 0 THEN EXIT SUB
        END IF
      NEXT K
      END IF
    NEXT J
    NEXT I
    PRINT "No Answer."
END SUB

ON ERROR GOTO DOERROR
MAIN
GOTO FINISH
DOERROR:
RESUME NEXT
FINISH:
