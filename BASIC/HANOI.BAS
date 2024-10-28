DEFLNG A-Z
DIM T$(2, 3)
T$(0, 0) = "A": T$(0, 1) = "C": T$(0, 2) = "B"
T$(1, 0) = "A": T$(1, 1) = "B": T$(1, 2) = "C"
PRINT "": PRINT "*** Tower of Hanoi Solver ***"
INPUT "Layers (3-30): ", N
IF N < 3 OR N > 30 THEN
  PRINT "Layers not in range."
  END
END IF
STEPS = 2 ^ N - 1
ST = 1: FIN = STEPS
PRINT "Total steps:"; STEPS
INPUT "Steps range (Start, End):", ST, FIN
IF ST < 1 OR ST > FIN OR FIN > STEPS THEN
  PRINT "Invalid steps range."
  END
END IF
CNT = 1
FOR X = ST TO FIN
  SRC$ = T$(N AND 1, (X AND (X - 1)) MOD 3)
  DST$ = T$(N AND 1, ((X OR (X - 1)) + 1) MOD 3)
  PRINT USING "##########:"; X;
  PRINT SRC$; "->"; DST$; " ";
  CL = CNT MOD 5
  IF CL = 0 THEN PRINT "" ELSE PRINT TAB(CL * 16 + 1);
  IF (CNT MOD (23 * 5)) = 0 THEN
    PRINT "Press any key to continue";
    WHILE INPUT$(1) = "": WEND
    PRINT ""
  END IF
  CNT = CNT + 1
NEXT X
IF ((CNT - 1) MOD 5) <> 0 THEN PRINT ""
END

