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
DECLARE SUB TestTX ()
DECLARE FUNCTION n$ (n%)
DECLARE SUB TX (s AS STRING)
DECLARE SUB DrawText (x AS INTEGER, y AS INTEGER, text AS STRING)
DATA &H50,&H53,&H56,&HBE,&H00,&H00,&H2E,&HC7,&H04,&H00,&H00,&HB8,&H00,&HDB,&HCD,&H2F
DATA &H3C,&HFF,&H75,&H12,&H81,&HFB,&H50,&H54,&H75,&H0C,&HB8,&H11,&H00,&HCD,&H79,&H75
DATA &H05,&h2E,&HC7,&H04,&H01,&H00,&H5E,&H5B,&H58,&HCB
DATA &H1E,&H6,&H56,&H57,&H50,&H53,&HBE,&H0,&H0,&HBF,&H0,&H0,&HB8,&H0,&H0,&HBB,&H0,&H0,&H8E,&HD8,&H8E,&HC3,&HCD,&H7E,&H5B,&H58,&H5F,&H5E,&H7,&H1F,&HCB
DATA &H1E,&H6,&H56,&H57,&H50,&HBE,&H0,&H0,&HB8,&H0,&H0,&H8E,&HD8,&HBF,&H0,&H0,&HB8,&H0,&H0,&H8E,&HC0,&H53,&H51,&H52,&H8B,&H44,&H2,&H2E,&HA3,&H56,&H1,&H8B
DATA &H54,&H6,&H8A,&H44,&H8,&H8B,&H4C,&H4,&H8B,&H1C,&HB4,&H80,&H50,&H26,&H22,&H25,&H74,&H4,&HB4,&HC,&HCD,&H10,&H58,&H4B,&H74,&HB,&H41,&H80,&HFC,&H1,&H75,&H1
DATA &H47,&HD0,&HCC,&HEB,&HE7,&H47,&H42,&H83,&H6C,&H2,&H1,&H75,&HD8,&H5A,&H59,&H5B,&H58,&H5F,&H5E,&H7,&H1F,&HCB,&H0,&H0

DIM SHARED ASMINT7E(15)
DIM SHARED ASMDRAW(44)
TYPE FontDataT
    CH0 AS STRING * 1
    CH1 AS STRING * 1
    FONT AS INTEGER
    W AS INTEGER
    H AS INTEGER
    TOP AS INTEGER
    BOTTOM AS INTEGER
    ATTR AS INTEGER
    BUFLEN AS INTEGER
END TYPE
TYPE DrawBitmapT
    W AS INTEGER
    H AS INTEGER
    X AS INTEGER
    Y AS INTEGER
    C AS STRING*1
END TYPE
DIM SHARED BITMAP(8194) AS INTEGER

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

SUB TX (s AS STRING)
    PRINT #1, CHR$(14); "["; s; "]";
END SUB
SUB DrawStr(STR AS STRING, X1 AS INTEGER, Y1 AS INTEGER, W AS INTEGER, H AS INTEGER, FONTASC AS INTEGER, FONTHZK AS INTEGER, ATTR AS INTEGER, DIST AS INTEGER, C AS INTEGER)
    I=0: L=LEN(STR): XA=X1: FONT=0
    WHILE I<L
        CH$=MID$(STR,I+1,1): FONT=FONTASC: WA=W
        IF ASC(CH$)>=&H80 THEN
            I=I+1: CH$=CH$+MID$(STR,I+1,1): FONT=FONTHZK
        END IF
        CALL GetChar(CH$,FONT,WA,H,ATTR)
        CALL DrawChar(WA,H,XA,Y1,C)
        DX=WA+DIST: IF DX>0 THEN XA=XA+DX
        I=I+1
    WEND
END SUB
SUB GetChar(STR AS STRING,FONT AS INTEGER,W AS INTEGER,H AS INTEGER,ATTR AS INTEGER)
    STATIC Param AS FontDataT
    IF ASC(MID$(STR,1,1)) < &H80 THEN
        Param.CH0=STR: Param.CH1=CHR$(0)
        Param.W=W
    ELSE
        Param.CH0=MID$(STR,2,1): Param.CH1=MID$(STR,1,1)
        Param.W=W*2
    END IF
    Param.FONT=FONT: Param.H=H
    Param.TOP=0: Param.BOTTOM=H-1
    Param.ATTR=ATTR: Param.BUFLEN=16384
    DS=VARSEG(Param): ES=VARSEG(BITMAP(0))
    SI=VARPTR(Param): DI=VARPTR(BITMAP(0))
    DEF SEG=VARSEG(SI): SI0=PEEK(VARPTR(SI)): SI1=PEEK(VARPTR(SI)+1)
    DEF SEG=VARSEG(DI): DI0=PEEK(VARPTR(DI)): DI1=PEEK(VARPTR(DI)+1)
    DEF SEG=VARSEG(DS): DS0=PEEK(VARPTR(DS)): DS1=PEEK(VARPTR(DS)+1)
    DEF SEG=VARSEG(ES): ES0=PEEK(VARPTR(ES)): ES1=PEEK(VARPTR(ES)+1)
    DEF SEG=VARSEG(ASMINT7E(0)): OFFSET=VARPTR(ASMINT7E(0))
    POKE OFFSET+7, SI0: POKE OFFSET+8, SI1
    POKE OFFSET+10, DI0: POKE OFFSET+11, DI1
    POKE OFFSET+13, DS0: POKE OFFSET+14, DS1
    POKE OFFSET+16, ES0: POKE OFFSET+17, ES1
    CALL ABSOLUTE(OFFSET): DEF SEG
    W=Param.W
END SUB
SUB DrawChar(W AS INTEGER, H AS INTEGER, X AS INTEGER, Y AS INTEGER, C AS INTEGER)
    STATIC Param AS DrawBitmapT
    Param.W=W: Param.H=H: Param.X=X: Param.Y=Y: Param.C=CHR$(C)
    DS=VARSEG(Param): ES=VARSEG(BITMAP(0))
    SI=VARPTR(Param): DI=VARPTR(BITMAP(0))
    DEF SEG=VARSEG(SI): SI0=PEEK(VARPTR(SI)): SI1=PEEK(VARPTR(SI)+1)
    DEF SEG=VARSEG(DI): DI0=PEEK(VARPTR(DI)): DI1=PEEK(VARPTR(DI)+1)
    DEF SEG=VARSEG(DS): DS0=PEEK(VARPTR(DS)): DS1=PEEK(VARPTR(DS)+1)
    DEF SEG=VARSEG(ES): ES0=PEEK(VARPTR(ES)): ES1=PEEK(VARPTR(ES)+1)
    DEF SEG=VARSEG(ASMDRAW(0)): OFFSET=VARPTR(ASMDRAW(0))
    POKE OFFSET+6, SI0: POKE OFFSET+7, SI1
    POKE OFFSET+9, DS0: POKE OFFSET+10, DS1
    POKE OFFSET+14, DI0: POKE OFFSET+15, DI1
    POKE OFFSET+17, ES0: POKE OFFSET+18, ES1
    CALL ABSOLUTE(OFFSET)
    DEF SEG
END SUB
SUB DisplayData(DT AS STRING)
  STATIC PRM AS STRING, TEXTDISP AS STRING
  IF INSTR(DT,"$$")=0 THEN CALL TX(DT): EXIT SUB
  SEP=INSTR(3,DT,"|"): IF SEP=0 THEN EXIT SUB
  PRM=MID$(DT,3,SEP-3): TEXTDISP=MID$(DT,SEP+1)
  P=1: IF PRM="" OR TEXTDISP="" THEN EXIT SUB
  REM XPos
  SEP=INSTR(P,PRM,","): IF SEP=0 THEN EXIT SUB
  X=VAL(MID$(PRM,P,SEP-P)): P=SEP+1
  REM YPos
  SEP=INSTR(P,PRM,","): IF SEP=0 THEN EXIT SUB
  Y=VAL(MID$(PRM,P,SEP-P)): P=SEP+1
  REM Width
  SEP=INSTR(P,PRM,","): IF SEP=0 THEN EXIT SUB
  W=VAL(MID$(PRM,P,SEP-P)): P=SEP+1
  REM Height
  SEP=INSTR(P,PRM,","): IF SEP=0 THEN EXIT SUB
  H=VAL(MID$(PRM,P,SEP-P)): P=SEP+1
  REM Font
  SEP=INSTR(P,PRM,","): IF SEP=0 THEN EXIT SUB
  FONTS$=MID$(PRM,P,SEP-P): P=SEP+1
  FONTH=VAL(MID$(FONTS$,2)): FONTA=ASC(MID$(FONTS$,1,1))-&H41
  REM ATTR
  SEP=INSTR(P,PRM,","): IF SEP=0 THEN EXIT SUB
  ATTR=VAL(MID$(PRM,P,SEP-P)): P=SEP+1
  REM Distance
  SEP=INSTR(P,PRM,","): IF SEP=0 THEN EXIT SUB
  DIST=VAL(MID$(PRM,P,SEP-P)): P=SEP+1
  REM COLOR
  CL=VAL(MID$(PRM,P))
  CALL DrawStr(TEXTDISP,X,Y,W,H,FONTA,FONTH,ATTR,DIST,CL)
END SUB
SUB DisplaySlide (ID AS INTEGER)
    S=SLIDE(ID).LSTART
    E=SLIDE(ID).LEND
    IF S<E THEN
      FOR I = S TO E-1
        L=LEN(CONTENT(I)): P=1: DO: P2=INSTR(P+1,CONTENT(I),CHR$(&H0A))
          IF P2>0 THEN
            DT$=MID$(CONTENT(I),P,P2-P): P=P2+1
          ELSE
            DT$=MID$(CONTENT(I),P): P=0
          END IF
          CALL DisplayData(DT$)
        LOOP UNTIL (P=0)
      NEXT I
    END IF
    IF MUSIC(ID) <> "" THEN PLAY "MB": PLAY "X" + VARPTR$(MUSIC(ID))
END SUB

FUNCTION GetSlideIdx% (n AS STRING)
    GetSlideIdx% = -1
    FOR I = 0 TO SLIDECNT-1 STEP 1
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
  IF A%(49)=0 THEN PRINT "Please run TX.COM first": END
  OPEN "LPT3" FOR OUTPUT AS #1
  DEF SEG = VARSEG(ASMINT7E(0))
  FOR I% = 0 TO 30
    READ D%: POKE VARPTR(ASMINT7E(0)) + I%, D%
  NEXT I%
  DEF SEG = VARSEG(ASMDRAW(0))
  FOR I% = 0 TO 87
    READ D%: POKE VARPTR(ASMDRAW(0)) + I%, D%
  NEXT I%
  DEF SEG
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
      ELSEIF LEN(CONTENT(E-1)) + LEN(DATATEXT) > 256 THEN
        CONTENT(E-1) = CONTENT(E-1) + CHR$(&H0A) + DATATEXT
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
      IF INSTR(TARGET$, "EXT$")=1 THEN
        ACTIONARR(I).EXTERNAL = 1
        ACTIONARR(I).TARGET = RIGHT$(TARGET$, LEN(TARGET$) - 4)
      ELSE
        ACTIONARR(I).EXTERNAL = 0
        ACTIONARR(I).TARGET = TARGET$
      END IF
  END SELECT
END SUB

SUB LoadData (FILENAME AS STRING)
    STATIC INITOK AS INTEGER
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
  ON ERROR GOTO ERROREND
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
                CALL HandleKeyboard(K$)
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

SUB HandleKeyboard (K AS STRING)
    KEY$ = K
    IF ACTIONCNT > 0 THEN
        FOR I = 0 TO ACTIONCNT - 1 STEP 1
            IF ACTIONARR(I).SLIDE = CURRENTSLIDE THEN
                TRIGGER$ = RTRIM$(ACTIONARR(I).TRIGGER)
                IF TRIGGER$ = KEY$ THEN
                    CALL HandleTarget(ACTIONARR(I).TARGET, ACTIONARR(I).EXTERNAL)
                    EXIT SUB
                END IF
            END IF
        NEXT I
        FOR I = 0 TO ACTIONCNT - 1 STEP 1
            IF ACTIONARR(I).SLIDE = CURRENTSLIDE AND "ANYKEY" = RTRIM$(ACTIONARR(I).TRIGGER) THEN
                CALL HandleTarget(ACTIONARR(I).TARGET, ACTIONARR(I).EXTERNAL)
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

SUB HandleTarget (TARGET AS STRING, Ext AS INTEGER)
    IF "NULL" = TARGET THEN EXIT SUB
    IF Ext <> 0 THEN
        ACTION$ = "LOADPPT"
        FILENAME$ = LTRIM$(RTRIM$(TARGET))
    ELSE
        TARGETSLIDE = GetSlideIdx%(TARGET)
        IF TARGETSLIDE > -1 THEN CURRENTSLIDE = TARGETSLIDE: ACTION$ = "SWITCHSLIDE"
    END IF
END SUB

SUB PANIC(MSG AS STRING)
  TX("KB1,1M3CU1,1"): CLOSE
  CLS:LOCATE 1,1:PRINT MSG
  END
END SUB
