10 DEFINT A-Z: DIM T$(2,3)
20 T$(0,0)="A":T$(0,1)="C":T$(0,2)="B"
21 T$(1,0)="A":T$(1,1)="B":T$(1,2)="C"
30 PRINT "":PRINT "*** Tower of Hanoi Solver ***"
40 INPUT "Layers (3-14): ",N
50 IF N<3 OR N>14 THEN PRINT "Layers not in range.":END
60 STEPS=2^N-1:ST=1:FIN=STEPS
70 PRINT "Total steps:";STEPS:INPUT "Steps range (Start, End):",ST,FIN
80 IF ST<1 OR ST>FIN OR FIN>STEPS THEN PRINT "Invalid steps range.":END
90 CNT=1:FOR X=ST TO FIN
100 SRC$=T$(N AND 1, (X AND (X-1)) MOD 3)
110 DST$=T$(N AND 1, ((X OR (X-1))+1) MOD 3)
120 PRINT USING "#####:";X;:PRINT SRC$;"->";DST$;"  ";
130 IF (CNT MOD 6)=0 THEN PRINT ""
140 IF (CNT MOD (23*6)) = 0 THEN PRINT "Press any key to continue";:WHILE INPUT$(1)="":WEND:PRINT ""
150 CNT=CNT+1: NEXT X
160 IF ((CNT-1) MOD 6)<>0 THEN PRINT ""
170 END
