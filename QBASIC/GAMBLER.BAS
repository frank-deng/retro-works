DEFLNG A-Z
RANDOMIZE TIMER
INPUT "Money: ", M: INPUT "Bet: ", B0
R = 0
DO WHILE M > 0
  IF B0 > M THEN B = M ELSE B = B0
  IF RND < 0.5 THEN M = M - B ELSE M = M + B
  R = R + 1
  LOCATE ,1: PRINT "Round:";R;" Money:";M;
  IF INKEY$ = CHR$(27) THEN
    EXIT DO
  END IF
LOOP
LOCATE ,1
IF M > 0 THEN
  PRINT "You have";M;"after";R;"rounds."
ELSE
  PRINT "You are bankrupt after";R;"rounds."
END IF
END