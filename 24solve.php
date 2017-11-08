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
COMMON SHARED A,B,C,D,R,GOAL,CANS
CANS=0

SUB CALC
<?php foreach ($exprAll as $e){?>
    R=<?=sprintf($e[expr],'A','B','C','D')?>:IF R=GOAL THEN PRINT <?=str_replace('"";','',sprintf('"'.$e[expr].'=";R','";A;"','";B;"','";C;"','";D;"'))?>:GOTO FOUND
<?php } ?>
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