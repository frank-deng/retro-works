DEFINT A-Z
TYPE REGSTYPE
  AX AS INTEGER
  BX AS INTEGER
  CX AS INTEGER
  DX AS INTEGER
  BP AS INTEGER
  SI AS INTEGER
  DI AS INTEGER
  DS AS INTEGER
  ES AS INTEGER
  FLAGS AS INTEGER
END TYPE
DECLARE SUB INTX(N AS INTEGER,REGS AS REGSTYPE)

DECLARE SUB INITENV()
DECLARE SUB LoadData (FILENAME AS STRING)
DECLARE SUB MainLoop ()
DECLARE SUB ProcessLine (MODE AS STRING, DATATEXT AS STRING)
DECLARE SUB DisplaySlide (ID AS INTEGER)
DECLARE FUNCTION GetSlideIdx% (n AS STRING)
DECLARE SUB ProcessTarget (TARGET AS STRING, Ext AS INTEGER)
DECLARE SUB ProcessKeyboard (K AS STRING)
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
TYPE FontFormatT
  X AS INTEGER
  Y AS INTEGER
  W AS INTEGER
  H AS INTEGER
  FASC AS INTEGER
  FHZK AS INTEGER
  ATTR AS INTEGER
  SP AS INTEGER
  CL AS INTEGER
END TYPE
COMMON SHARED REGS AS REGSTYPE
COMMON SHARED FFMT AS FontFormatT
COMMON SHARED SLIDECNT, ACTIONCNT, CURRENTSLIDE, ACTION$, INITCMD AS STRING, FILENAME$
DECLARE FUNCTION n$ (n%)
DECLARE SUB TX (s AS STRING)
DECLARE SUB DrawText (x AS INTEGER, y AS INTEGER, text AS STRING)

DIM SHARED ASMINTX(37),ASMDRAW(44)
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

FFMT.W=16
FFMT.H=16
FFMT.ATTR=1
FFMT.CL=7
CALL INITENV
OPEN "LPT3" FOR OUTPUT AS #1
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
    REGS.DS=VARSEG(Param): REGS.ES=VARSEG(BITMAP(0))
    REGS.SI=VARPTR(Param): REGS.DI=VARPTR(BITMAP(0))
    CALL INTX(&H7E,REGS)
    W=Param.W
END SUB
SUB DrawChar(W AS INTEGER, H AS INTEGER, X AS INTEGER, Y AS INTEGER, C AS INTEGER)
    STATIC Param AS DrawBitmapT
    Param.W=W: Param.H=H: Param.X=X: Param.Y=Y: Param.C=CHR$(C)
    ASMDRAW(1)=VARPTR(Param): ASMDRAW(3)=VARPTR(BITMAP(0))
    ASMDRAW(5)=VARSEG(Param): ASMDRAW(7)=VARSEG(BITMAP(0))
    DEF SEG=VARSEG(ASMDRAW(0)): CALL ABSOLUTE(VARPTR(ASMDRAW(0))): DEF SEG
END SUB
SUB ParseFontParam(S AS STRING)
  STATIC CMD AS STRING, PARAM AS STRING, IDX AS INTEGER
  IDX=1:WHILE IDX<=LEN(S)
  DO
    CMD=MID$(S,IDX,1): IDX=IDX+1
  LOOP WHILE INSTR("-|@=#^(",CMD)=0
  ISTART=IDX
  WHILE IDX<=LEN(S) AND INSTR("0123456789,",MID$(S,IDX,1))<>0
    IDX=IDX+1
  WEND
  PARAM=MID$(S,ISTART,IDX-ISTART)
  SELECT CASE CMD
    CASE "|"
      FFMT.Y=VAL(PARAM)
    CASE "-"
      FFMT.X=VAL(PARAM)
    CASE "@"
      SEP=INSTR(PARAM,",")
      IF SEP=0 THEN
        FFMT.W=VAL(PARAM)/2: FFMT.H=VAL(PARAM)
      ELSE
        FFMT.W=VAL(MID$(PARAM,1,SEP-1)): FFMT.H=VAL(MID$(PARAM,SEP+1))
      END IF
    CASE "="
      SEP=INSTR(PARAM,",")
      IF SEP=0 THEN
        FFMT.FASC=VAL(PARAM)
      ELSE
        FFMT.FASC=VAL(MID$(PARAM,1,SEP-1)): FFMT.FHZK=VAL(MID$(PARAM,SEP+1))
      END IF
    CASE "#"
      FFMT.ATTR=VAL(PARAM)
    CASE "^"
      FFMT.SP=VAL(PARAM)
    CASE "("
      FFMT.CL=VAL(PARAM)
  END SELECT
  WEND
END SUB
SUB DisplayData(DT AS STRING)
  STATIC PRM AS STRING, TEXTDISP AS STRING
  IF INSTR(DT,"$$")=0 THEN CALL TX(DT): EXIT SUB
  SEP=INSTR(3,DT,":")
  IF SEP=0 THEN
    CALL ParseFontParam(MID$(DT,3))
    EXIT SUB
  ELSE
    CALL ParseFontParam(MID$(DT,3,SEP-3))
    TEXTDISP=MID$(DT,SEP+1)
    CALL DrawStr(TEXTDISP,FFMT.X,FFMT.Y,FFMT.W,FFMT.H,FFMT.FASC,FFMT.FHZK,FFMT.ATTR,FFMT.SP,FFMT.CL)
  END IF
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

DATA &H56,&HBE,&H0,&H0,&H50,&HB8,&H0,&H0,&H53,&H51,&H52,&H55,&H57,&H1E,&H6
DATA &H8E,&HD8,&HB9,&H9,&H0,&HFF,&H34,&H46,&H46,&HE2,&HFA,&H7,&H1F,&H5F,&H5E
DATA &H5D,&H5A,&H59,&H5B,&H58,&HCD,&H0,&H9C,&H6,&H1E,&H57,&H56,&H55,&H52,&H51
DATA &H53,&H50,&HB8,&H0,&H0,&H8E,&HD8,&HB9,&HA,&H0,&HBE,&H0,&H0,&H8F,&H4,&H46
DATA &H46,&HE2,&HFA,&H7,&H1F,&H5F,&H5D,&H5A,&H59,&H5B,&H58,&H5E,&HCB

DATA &H56,&HBE,&H0,&H0,&H57,&HBF,&H0,&H0,&H50,&HB8,&H0,&H0,&H53,&HBB,&H0,&H0
DATA &H51,&H52,&H1E,&H6,&H55,&HFF,&H74,&H2,&H8E,&HD8,&H8E,&HC3,&HB4,&HC,&H8A
DATA &H44,&H8,&H8B,&H54,&H6,&H8B,&H4C,&H4,&H8B,&H2C,&HB7,&H80,&H8A,&HDF,&H26
DATA &H22,&H1D,&H74,&H2,&HCD,&H10,&H4D,&H74,&HB,&H41,&H80,&HFF,&H1,&H75,&H1
DATA &H47,&HD0,&HCF,&HEB,&HE9,&H47,&H42,&H83,&H6C,&H2,&H1,&H75,&HDA,&H8F,&H44
DATA &H2,&H5D,&H7,&H1F,&H5A,&H59,&H5B,&H58,&H5F,&H5E,&HCB

SUB INITENV()
  DEF SEG = VARSEG(ASMINTX(0)): P = VARPTR(ASMINTX(0))
  FOR I = 0 TO 73: READ V: POKE P+I, V: NEXT I
  DEF SEG = VARSEG(ASMDRAW(0)): P = VARPTR(ASMDRAW(0))
  FOR I = 0 TO 86: READ V: POKE P+I, V: NEXT I
  DEF SEG
  REGS.AX=&HDB00:CALL INTX(&H2F,REGS)
  IF (REGS.AX AND 255)<>255 OR REGS.BX<>&H5450 THEN
    PRINT "Please run UCDOS first.":END
  END IF
  REGS.AX=&H11:CALL INTX(&H79,REGS)
  IF (REGS.FLAGS AND &H40)=0 THEN
    PRINT "Please run TX.COM first.": END
  END IF
END SUB

SUB INTX (N AS INTEGER, REGS AS REGSTYPE)
  STATIC DS AS INTEGER,SI AS INTEGER,P AS INTEGER
  DS=VARSEG(REGS):SI=VARPTR(REGS)
  ASMINTX(1)=SI:ASMINTX(3)=DS
  ASMINTX(24)=DS:ASMINTX(28)=SI
  DEF SEG=VARSEG(ASMINTX(0)):P=VARPTR(ASMINTX(0))
  POKE P+&H24,N:CALL ABSOLUTE(P):DEF SEG
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
