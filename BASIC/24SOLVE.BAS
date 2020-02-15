DEFINT I-K
COMMON SHARED goal, FOUND
DECLARE FUNCTION comp (A!, B!)
DECLARE FUNCTION calc! (A!, B!, o$)
DECLARE FUNCTION expr1! (A!, B!, C!, D!, O1$, O2$, O3$)
DECLARE FUNCTION expr2! (A!, B!, C!, D!, O1$, O2$, O3$)
DECLARE FUNCTION expr3! (A!, B!, C!, D!, O1$, O2$, O3$)
DECLARE FUNCTION expr4! (A!, B!, C!, D!, O1$, O2$, O3$)
DECLARE FUNCTION expr5! (A!, B!, C!, D!, O1$, O2$, O3$)

DECLARE SUB enumoper (A!, B!, C!, D!)
DECLARE SUB main ()

CALL main

FUNCTION calc! (A!, B!, o$)
  SELECT CASE o$
    CASE "+"
      calc! = A! + B!
    CASE "-"
      calc! = A! - B!
    CASE "*"
      calc! = A! * B!
    CASE "/"
      IF B! = 0 THEN
        calc! = 1000000
      ELSE
        calc! = A! / B!
      END IF
  END SELECT
END FUNCTION

FUNCTION comp (A!, B!)
  IF ABS(A! - B!) < .0001 THEN
    comp = 1
  ELSE
    comp = 0
  END IF
END FUNCTION

SUB enumoper (A AS SINGLE, B AS SINGLE, C AS SINGLE, D AS SINGLE)
  DIM o(4) AS STRING: o(0) = "+": o(1) = "-": o(2) = "*": o(3) = "/"
  FOR i = 0 TO 3: FOR j = 0 TO 3: FOR k = 0 TO 3
    IF comp(expr1(A, B, C, D, o(i), o(j), o(k)), goal) THEN
      PRINT A; o(i); "("; B; o(j); "("; C; o(k); D; "))="; goal
      FOUND = 1
      EXIT SUB
    ELSEIF comp(expr2(A, B, C, D, o(i), o(j), o(k)), goal) THEN
      PRINT A; o(i); "(("; B; o(j); C; ")"; o(k); D; ")="; goal
      FOUND = 1
      EXIT SUB
    ELSEIF comp(expr3(A, B, C, D, o(i), o(j), o(k)), goal) THEN
      PRINT "("; A; o(i); "("; B; o(j); C; "))"; o(k); D; "="; goal
      FOUND = 1
      EXIT SUB
    ELSEIF comp(expr4(A, B, C, D, o(i), o(j), o(k)), goal) THEN
      PRINT "("; A; o(i); B; ")"; o(j); "("; C; o(k); D; ")="; goal
      FOUND = 1
      EXIT SUB
    ELSEIF comp(expr5(A, B, C, D, o(i), o(j), o(k)), goal) THEN
      PRINT "(("; A; o(i); B; ")"; o(j); C; ")"; o(k); D; "="; goal
      FOUND = 1
      EXIT SUB
    END IF
  NEXT k: NEXT j: NEXT i
END SUB

FUNCTION expr1! (A!, B!, C!, D!, O1$, O2$, O3$)
  REM abcd### a#(b#(c#d))
  expr1! = calc!(A!, calc!(B!, calc!(C!, D!, O3$), O2$), O1$)
END FUNCTION

FUNCTION expr2! (A!, B!, C!, D!, O1$, O2$, O3$)
  REM abc#d## a#((b#c)#d)
  expr2! = calc!(A!, calc!(calc!(B!, C!, O2$), D!, O3$), O1$)
END FUNCTION

FUNCTION expr3! (A!, B!, C!, D!, O1$, O2$, O3$)
  REM abc##d# (a#(b#c))#d
  expr3! = calc!(calc!(A!, calc!(B!, C!, O2$), O1$), D!, O3$)
END FUNCTION

FUNCTION expr4! (A!, B!, C!, D!, O1$, O2$, O3$)
  REM ab#cd## (a#b)#(c#d)
  expr4! = calc!(calc!(A!, B!, O1$), calc!(C!, D!, O3$), O2$)
END FUNCTION

FUNCTION expr5! (A!, B!, C!, D!, O1$, O2$, O3$)
  REM ab#c#d# ((a#b)#c)#d
  expr5! = calc!(calc!(calc!(A!, B!, O1$), C!, O2$), D!, O3$)
END FUNCTION

SUB main
  DIM N(4) AS SINGLE: FOUND = 0
  INPUT "A,B,C,D,Goal:", N(0), N(1), N(2), N(3), goal
  FOR i = 0 TO 3: FOR j = 0 TO 3
    IF i <> j THEN
      FOR k = 0 TO 3
        IF i <> k AND j <> k THEN
          CALL enumoper(N(i), N(j), N(k), N(6 - i - j - k))
          IF FOUND > 0 THEN EXIT SUB
        END IF
      NEXT k
    END IF
  NEXT j: NEXT i
  PRINT "No Answer"
END SUB

