DECLARE SUB InitTX ()
DECLARE SUB LoadData (FILENAME AS STRING)
DECLARE SUB MainLoop ()
DECLARE SUB ProcessLine (MODE AS STRING, DATATEXT AS STRING)
DECLARE SUB DisplaySlide (ID AS INTEGER)
DECLARE FUNCTION GetSlideIdx% (n AS STRING)
DECLARE SUB ProcessTarget (TARGET AS STRING, Ext AS INTEGER)
DECLARE SUB ProcessKeyboard (K AS STRING)
DEFINT A-Z
TYPE SlideT
  SNAME AS STRING*40
  LSTART AS INTEGER
  LEND AS INTEGER
END TYPE
TYPE ActionT
  SLIDE AS INTEGER
  EXTERNAL AS INTEGER
  TARGET AS STRING * 40
  TRIGGER AS STRING * 10
END TYPE
COMMON SHARED SLIDECNT, ACTIONCNT, CURRENTSLIDE, ACTION$, INITCMD AS STRING, FILENAME$
COMMON INITOK
DECLARE SUB TestTX ()
DECLARE FUNCTION n$ (n%)
DECLARE SUB TX (s AS STRING)
DECLARE SUB DrawText (x AS INTEGER, y AS INTEGER, text AS STRING)
DATA &H50,&H53,&H56,&HBE,&H00,&H00,&H2E,&HC7,&H04,&H00,&H00,&HB8,&H00,&HDB,&HCD,&H2F
DATA &H3C,&HFF,&H75,&H12,&H81,&HFB,&H50,&H54,&H75,&H0C,&HB8,&H11,&H00,&HCD,&H79,&H75
DATA &H05,&h2E,&HC7,&H04,&H01,&H00,&H5E,&H5B,&H58,&HCB

ON ERROR GOTO ERROREND

DIM SHARED SLIDE(64) AS SlideT
DIM SHARED CONTENT(2048) AS STRING
DIM SHARED ACTIONARR(512) AS ActionT
DIM SHARED MUSIC(64) AS STRING

CALL InitTX
CLS : INPUT "请输入文件名：", FILENAME$
IF FILENAME$ = "" THEN FILENAME$ = "PPT.TXT"
PRINT "加载中……"
CALL LoadData(FILENAME$)
CALL MainLoop
TX ("KB1,1M3CU1,1")
CLOSE
END

ERROREND:
ERRVAL = ERR
TX ("KB1,1M3CU1,1")
CLOSE
PRINT "Error:"; ERRVAL; ERL
END

SUB DisplaySlide (ID AS INTEGER)
    S=SLIDE(ID).LSTART
    E=SLIDE(ID).LEND
    IF S<E THEN
      FOR I = S TO E-1
        CALL TX(CONTENT(I))
      NEXT I
    END IF
    IF MUSIC(ID) <> "" THEN PLAY "MB": PLAY "X" + VARPTR$(MUSIC(ID))
END SUB

FUNCTION GetSlideIdx% (n AS STRING)
    GetSlideIdx% = -1
    FOR I = 0 TO SLIDECNT-1 STEP 1
        rem print "<";n;"|";SLIDE(I).SNAME;">"
        IF RTRIM$(n) = RTRIM$(SLIDE(I).SNAME) THEN
            GetSlideIdx% = I: EXIT FUNCTION
        END IF
    NEXT I
END FUNCTION

SUB InitTX
    DIM A%(50)
    DEF SEG = VARSEG(A%(0))
    RESTORE
    FOR I% = 0 TO 41
        READ D%
        IF I% = 4 THEN
        D% = VARPTR(A%(49)) MOD 256
        ELSEIF I% = 5 THEN
        D% = VARPTR(A%(49)) / 256
        END IF
        POKE VARPTR(A%(0)) + I%, D%
    NEXT I%
    CALL ABSOLUTE(VARPTR(A%(0)))
    DEF SEG
    IF A%(49) = 0 THEN
        PRINT "Please run TX.COM first"
    END
    END IF
    OPEN "LPT3" FOR OUTPUT AS #1
END SUB

SUB ProcessLine (MODE AS STRING, DATATEXT AS STRING)
    SELECT CASE MODE
        CASE ".INIT"
            INITCMD = INITCMD + DATATEXT
        CASE ".CONTENT"
            E=SLIDE(SLIDECNT-1).LEND
            IF SLIDE(SLIDECNT-1).LSTART=E THEN
                CONTENT(E) = DATATEXT
                SLIDE(SLIDECNT-1).LEND=E+1
            ELSEIF LEN(CONTENT(E-1)) + LEN(DATATEXT) < 256 THEN
                CONTENT(E-1) = CONTENT(E-1) + DATATEXT
            ELSE
                CONTENT(E) = DATATEXT
                SLIDE(SLIDECNT-1).LEND=E+1
            END IF
        CASE ".MUSIC"
            MUSIC(SLIDECNT - 1) = MUSIC(SLIDECNT - 1) + DATATEXT
        CASE ".ACTION"
            ACTIONCNT = ACTIONCNT + 1: I = ACTIONCNT - 1
            ACTIONARR(I).SLIDE = SLIDECNT - 1
            ACTIONARR(I).TRIGGER = LEFT$(DATATEXT, INSTR(DATATEXT, ":") - 1)
            TARGET$ = RIGHT$(DATATEXT, LEN(DATATEXT) - INSTR(DATATEXT, ":"))
            IF INSTR(TARGET$, "EXT$") > 0 THEN
                ACTIONARR(I).EXTERNAL = 1
                ACTIONARR(I).TARGET = RIGHT$(TARGET$, LEN(TARGET$) - 4)
            ELSE
                ACTIONARR(I).EXTERNAL = 0
                ACTIONARR(I).TARGET = TARGET$
            END IF
    END SELECT
END SUB

SUB LoadData (FILENAME AS STRING)
    INITOK=0
    INITCMD = ""
    SLIDECNT = 0
    ACTIONCNT = 0
    CURRENTSLIDE = 0
    ACTION$ = ""
    OPEN FILENAME FOR INPUT AS #2
    MODE$ = ""
    DO
        LINE INPUT #2, DATATEXT$
        DATATEXT$ = LTRIM$(RTRIM$(DATATEXT$))
        SELECT CASE DATATEXT$
            CASE ""
            CASE ".SLIDE"
                IF SLIDECNT>65 THEN PANIC("最多支持65页")
                SLIDECNT = SLIDECNT + 1
                I=SLIDECNT-1
                LINE INPUT #2, DATATEXT$
                SLIDE(I).SNAME=DATATEXT$
                IF I=0 THEN
                  SLIDE(I).LSTART=0
                ELSE
                  SLIDE(I).LSTART=SLIDE(I-1).LEND
                END IF
                SLIDE(I).LEND=SLIDE(I).LSTART
                LCOUNT=0
            CASE ".INIT"
                IF INITOK=1 THEN PANIC("只允许出现1次.INIT")
                INITOK=1
                MODE$ = DATATEXT$
            CASE ".CONTENT"
                MODE$ = DATATEXT$
            CASE ".ACTION"
                MODE$ = DATATEXT$
            CASE ".MUSIC"
                MODE$ = DATATEXT$
            CASE ELSE
                CALL ProcessLine(MODE$, DATATEXT$)
        END SELECT
    LOOP UNTIL (EOF(2))
    CLOSE #2
END SUB

SUB MainLoop
    TX (INITCMD)
    CALL DisplaySlide(CURRENTSLIDE)
    DO
        'Handle keyboard action
        K$ = ""
        DO
            K$ = INKEY$
        LOOP WHILE K$ = ""

        SELECT CASE K$
            CASE " "
                K$ = "SPACE"
            CASE CHR$(27)
                K$ = "ESC"
            CASE CHR$(9)
                K$ = "TAB"
            CASE CHR$(0) + "G"
                K$ = "HOME"
            CASE CHR$(0) + "O"
                K$ = "END"
            CASE CHR$(0) + "I"
                K$ = "PAGEUP"
            CASE CHR$(0) + "Q"
                K$ = "PAGEDOWN"
            CASE CHR$(0) + "H"
                K$ = "UP"
            CASE CHR$(0) + "P"
                K$ = "DOWN"
            CASE CHR$(0) + "K"
                K$ = "LEFT"
            CASE CHR$(0) + "M"
                K$ = "RIGHT"
            CASE CHR$(0) + "R"
                K$ = "INSERT"
            CASE CHR$(0) + "S"
                K$ = "DELETE"
            CASE CHR$(0) + ";"
                K$ = "F1"
            CASE CHR$(0) + "<"
                K$ = "F2"
            CASE CHR$(0) + "="
                K$ = "F3"
            CASE CHR$(0) + ">"
                K$ = "F4"
            CASE CHR$(0) + "?"
                K$ = "F5"
            CASE CHR$(0) + "@"
                K$ = "F6"
            CASE CHR$(0) + "A"
                K$ = "F7"
            CASE CHR$(0) + "B"
                K$ = "F8"
            CASE CHR$(0) + "C"
                K$ = "F9"
            CASE CHR$(0) + "D"
                K$ = "F10"
            CASE CHR$(0) + CHR$(133)
                K$ = "F11"
            CASE CHR$(0) + CHR$(134)
                K$ = "F12"
        END SELECT

        SELECT CASE K$
            CASE ""
            CASE "ESC"
                EXIT SUB
            CASE "HOME"
                CURRENTSLIDE = 0: ACTION$ = "SWITCHSLIDE"
            CASE "END"
                CURRENTSLIDE = SLIDECNT - 1: ACTION$ = "SWITCHSLIDE"
            CASE "PAGEUP"
                IF CURRENTSLIDE > 0 THEN CURRENTSLIDE = CURRENTSLIDE - 1: ACTION$ = "SWITCHSLIDE"
            CASE "PAGEDOWN"
                IF CURRENTSLIDE < SLIDECNT - 1 THEN CURRENTSLIDE = CURRENTSLIDE + 1: ACTION$ = "SWITCHSLIDE"
            CASE ELSE
                CALL ProcessKeyboard(K$)
        END SELECT

        SELECT CASE ACTION$
            CASE "SWITCHSLIDE"
                ACTION$ = ""
                CALL DisplaySlide(CURRENTSLIDE)
            CASE "LOADPPT"
                ACTION$ = ""
                CALL LoadData(FILENAME$)
                CALL DisplaySlide(CURRENTSLIDE)
        END SELECT
        ACTION$ = ""
    LOOP
END SUB

FUNCTION n$ (A AS INTEGER)
n$ = LTRIM$(RTRIM$(STR$(A)))
END FUNCTION

SUB ProcessKeyboard (K AS STRING)
    KEY$ = K
    IF ACTIONCNT > 0 THEN
        FOR I = 0 TO ACTIONCNT - 1 STEP 1
            IF ACTIONARR(I).SLIDE = CURRENTSLIDE THEN
                TRIGGER$ = RTRIM$(ACTIONARR(I).TRIGGER)
                IF TRIGGER$ = KEY$ THEN
                    CALL ProcessTarget(ACTIONARR(I).TARGET, ACTIONARR(I).EXTERNAL)
                    EXIT SUB
                END IF
            END IF
        NEXT I
        FOR I = 0 TO ACTIONCNT - 1 STEP 1
            IF ACTIONARR(I).SLIDE = CURRENTSLIDE AND "ANYKEY" = RTRIM$(ACTIONARR(I).TRIGGER) THEN
                CALL ProcessTarget(ACTIONARR(I).TARGET, ACTIONARR(I).EXTERNAL)
                EXIT SUB
            END IF
        NEXT I
    END IF
    SELECT CASE KEY$
        CASE "LEFT"
            IF CURRENTSLIDE > 0 THEN CURRENTSLIDE = CURRENTSLIDE - 1: ACTION$ = "SWITCHSLIDE"
        CASE "BACKSPACE"
            IF CURRENTSLIDE > 0 THEN CURRENTSLIDE = CURRENTSLIDE - 1: ACTION$ = "SWITCHSLIDE"
        CASE "RIGHT"
            IF CURRENTSLIDE < SLIDECNT - 1 THEN CURRENTSLIDE = CURRENTSLIDE + 1: ACTION$ = "SWITCHSLIDE"
        CASE "SPACE"
            IF CURRENTSLIDE < SLIDECNT - 1 THEN CURRENTSLIDE = CURRENTSLIDE + 1: ACTION$ = "SWITCHSLIDE"
    END SELECT
END SUB

SUB ProcessTarget (TARGET AS STRING, Ext AS INTEGER)
    IF "NULL" = TARGET THEN EXIT SUB
    IF Ext <> 0 THEN
        ACTION$ = "LOADPPT"
        FILENAME$ = LTRIM$(RTRIM$(TARGET))
    ELSE
        TARGETSLIDE = GetSlideIdx%(TARGET)
        IF TARGETSLIDE > -1 THEN CURRENTSLIDE = TARGETSLIDE: ACTION$ = "SWITCHSLIDE"
    END IF
END SUB

SUB TX (s AS STRING)
    PRINT #1, CHR$(14); "["; s; "]";
END SUB

SUB PANIC(MSG AS STRING)
  TX("KB1,1M3CU1,1"): CLOSE
  CLS:LOCATE 1,1:PRINT MSG
  END
END SUB
