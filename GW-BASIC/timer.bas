10 DEFINT A-Z:INPUT "Time: ",M!:S=M!*60
20 PRINT S;:ON TIMER(1) GOSUB 40:TIMER ON
30 WHILE INKEY$<>CHR$(27):WEND:END
40 IF S=0 THEN BEEP ELSE S=S-1
50 LOCATE ,1:PRINT S;:RETURN