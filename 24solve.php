#!/usr/bin/env php
<?php
$exprAll = [
    [expr=>"%s+%s+%s+%s", sort=>sort_abcd],
	[expr=>"%s+%s+%s-%s", sort=>sort_abc],
	[expr=>"%s+%s-%s-%s", sort=>sort_ab],
	[expr=>"%s-%s-%s-%s", sort=>null],

	[expr=>"%s*%s*%s*%s", sort=>sort_abcd],
	[expr=>"%s*%s*%s/%s", sort=>sort_abc],
	[expr=>"%s*%s/%s/%s", sort=>sort_ab],
	[expr=>"%s/%s/%s/%s", sort=>null],

	[expr=>"%s+%s+%s*%s", sort=>sort_ab_cd],
	[expr=>"(%s+%s+%s)*%s", sort=>sort_abc],
	[expr=>"%s+(%s+%s)*%s", sort=>sort_bc],
	[expr=>"(%s+%s)*(%s+%s)", sort=>sort_ab_cd],

	[expr=>"%s+%s*%s*%s", sort=>sort_bcd],
	[expr=>"(%s+%s)*%s*%s", sort=>sort_ab_cd],
	[expr=>"%s*%s+%s*%s", sort=>sort_ab_cd],
	[expr=>"(%s+%s*%s)*%s", sort=>sort_bc],

	[expr=>"%s+%s+%s/%s", sort=>sort_ab],
	[expr=>"%s+(%s+%s)/%s", sort=>sort_bc],
	[expr=>"%s+%s/(%s+%s)", sort=>sort_cd],
	[expr=>"(%s+%s+%s)/%s", sort=>sort_abc],
	[expr=>"%s/(%s+%s+%s)", sort=>sort_bcd],
	[expr=>"(%s+%s)/(%s+%s)", sort=>sort_ab_cd],

	[expr=>"%s+%s/%s/%s", sort=>null],
	[expr=>"(%s+%s)/%s/%s", sort=>sort_ab],
	[expr=>"%s/(%s+%s)/%s", sort=>sort_bc],
	[expr=>"%s/%s/(%s+%s)", sort=>sort_cd],
	[expr=>"(%s+%s/%s)/%s", sort=>null],
	[expr=>"%s/(%s+%s/%s)", sort=>null],
	[expr=>"%s/%s+%s/%s", sort=>null],

	[expr=>"%s-%s-%s*%s", sort=>sort_cd],
	[expr=>"%s-%s*%s-%s", sort=>sort_bc],
	[expr=>"%s*%s-%s-%s", sort=>sort_ab],
	[expr=>"%s-(%s-%s)*%s", sort=>null],
	[expr=>"(%s-%s)*%s-%s", sort=>null],
	[expr=>"(%s-%s-%s)*%s", sort=>null],
	[expr=>"(%s-%s)*(%s-%s)", sort=>null],

	[expr=>"%s-%s*%s*%s", sort=>sort_bcd],
	[expr=>"%s*%s*%s-%s", sort=>sort_abc],
	[expr=>"(%s-%s)*%s*%s", sort=>sort_cd],
	[expr=>"(%s-%s*%s)*%s", sort=>sort_bc],
	[expr=>"(%s*%s-%s)*%s", sort=>sort_ab],
	[expr=>"%s*%s-%s*%s", sort=>sort_ab_cd],

	[expr=>"%s-%s-%s/%s", sort=>null],
	[expr=>"%s-%s/%s-%s", sort=>null],
	[expr=>"%s/%s-%s-%s", sort=>null],
	[expr=>"%s-(%s-%s)/%s", sort=>null],
	[expr=>"%s-%s/(%s-%s)", sort=>null],
	[expr=>"(%s-%s)/%s-%s", sort=>null],
	[expr=>"%s/(%s-%s)-%s", sort=>null],
	[expr=>"(%s-%s-%s)/%s", sort=>null],
	[expr=>"%s/(%s-%s-%s)", sort=>null],
	[expr=>"(%s-%s)/(%s-%s)", sort=>null],

	[expr=>"%s-%s/%s/%s", sort=>null],
	[expr=>"%s/%s/%s-%s", sort=>null],
	[expr=>"%s/%s-%s/%s", sort=>null],
	[expr=>"(%s-%s)/%s/%s", sort=>null],
	[expr=>"%s/(%s-%s)/%s", sort=>null],
	[expr=>"%s/%s/(%s-%s)", sort=>null],
	[expr=>"(%s-%s/%s)/%s", sort=>null],
	[expr=>"(%s/%s-%s)/%s", sort=>null],
	[expr=>"%s/(%s-%s/%s)", sort=>null],
	[expr=>"%s/(%s/%s-%s)", sort=>null],

	[expr=>"%s+%s-%s*%s", sort=>sort_ab_cd],
	[expr=>"%s+%s*%s-%s", sort=>sort_bc],
	[expr=>"%s+(%s-%s)*%s", sort=>null],
	[expr=>"%s-(%s+%s)*%s", sort=>sort_bc],
	[expr=>"(%s+%s)*%s-%s", sort=>sort_ab],
	[expr=>"(%s+%s-%s)*%s", sort=>sort_ab],
	[expr=>"(%s+%s)*(%s-%s)", sort=>sort_ab],

	[expr=>"%s+%s-%s/%s", sort=>sort_ab],
	[expr=>"%s+%s/%s-%s", sort=>null],
	[expr=>"%s+(%s-%s)/%s", sort=>null],
	[expr=>"%s+%s/(%s-%s)", sort=>null],
	[expr=>"%s-(%s+%s)/%s", sort=>sort_bc],
	[expr=>"%s-%s/(%s+%s)", sort=>sort_cd],
	[expr=>"(%s+%s)/%s-%s", sort=>sort_ab],
	[expr=>"%s/(%s+%s)-%s", sort=>sort_bc],
	[expr=>"(%s+%s-%s)/%s", sort=>sort_ab],
	[expr=>"%s/(%s+%s-%s)", sort=>sort_bc],
	[expr=>"(%s+%s)/(%s-%s)", sort=>sort_ab],
	[expr=>"(%s-%s)/(%s+%s)", sort=>sort_cd],

	[expr=>"%s+%s*%s/%s", sort=>sort_bc],
	[expr=>"(%s+%s)*%s/%s", sort=>sort_ab],
	[expr=>"%s/(%s+%s)*%s", sort=>sort_bc],
	[expr=>"%s*%s+%s/%s", sort=>sort_ab],
	[expr=>"(%s+%s*%s)/%s", sort=>sort_bc],
	[expr=>"%s/(%s+%s*%s)", sort=>sort_cd],
	[expr=>"(%s+%s/%s)*%s", sort=>null],

	[expr=>"%s-%s*%s/%s", sort=>sort_bc],
	[expr=>"%s*%s/%s-%s", sort=>sort_ab],
	[expr=>"(%s-%s)*%s/%s", sort=>null],
	[expr=>"%s/(%s-%s)*%s", sort=>null],
	[expr=>"%s*%s-%s/%s", sort=>sort_ab],
	[expr=>"%s/%s-%s*%s", sort=>sort_cd],
	[expr=>"(%s-%s*%s)/%s", sort=>sort_bc],
	[expr=>"%s/(%s-%s*%s)", sort=>sort_cd],
	[expr=>"(%s*%s-%s)/%s", sort=>sort_ab],
	[expr=>"%s/(%s*%s-%s)", sort=>sort_bc],
	[expr=>"(%s-%s/%s)*%s", sort=>null],
];
?>DEFINT E-Z:DEFDBL A-D,R
COMMON SHARED A,B,C,D,R,GOAL,FOUND

SUB CALC
<?php foreach ($exprAll as $e){?>
    R=<?=sprintf($e[expr],'A','B','C','D')?>:IF R=GOAL THEN PRINT <?=str_replace('"";','',sprintf('"'.$e[expr].'=";R','";A;"','";B;"','";C;"','";D;"'))?>:GOTO LFOUND
<?php } ?>
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
