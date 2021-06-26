DEFINT A-Z
DO
  K$ = INKEY$
  SELECT CASE K$
    CASE ""
    CASE CHR$(27)
      EXIT DO
    CASE CHR$(0) + "H"
      PRINT "Up"
    CASE CHR$(0) + "P"
      PRINT "Down"
    CASE CHR$(0) + "K"
      PRINT "Left"
    CASE CHR$(0) + "M"
      PRINT "Right"
    CASE CHR$(0) + "G"
      PRINT "Home"
    CASE CHR$(0) + "O"
      PRINT "End"
    CASE CHR$(0) + "I"
      PRINT "Page Up"
    CASE CHR$(0) + "Q"
      PRINT "Page Down"
    CASE CHR$(0) + "R"
      PRINT "Insert"
    CASE CHR$(0) + "S"
      PRINT "Delete"
    CASE ELSE
      PRINT K$
  END SELECT
LOOP

