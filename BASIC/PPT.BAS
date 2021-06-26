DEFINT A-Z
TYPE ActionT
  SLIDE AS INTEGER
  EXTERNAL AS INTEGER
  TARGET AS STRING*40
  TRIGGER AS STRING*10
END TYPE
COMMON SHARED SLIDECOUNT,ACTIONCOUNT,CURRENTSLIDE,ACTION$,INITCMD AS STRING,FILENAME$
DECLARE SUB TestTX ()
DECLARE FUNCTION n$ (n%)
DECLARE SUB TX (s AS STRING)
DECLARE SUB DrawText(x as integer,y as integer,text as string)
DATA &H50,&H53,&H56,&HBE,&H00,&H00,&H2E,&HC7,&H04,&H00,&H00,&HB8,&H00,&HDB,&HCD,&H2F
DATA &H3C,&HFF,&H75,&H12,&H81,&HFB,&H50,&H54,&H75,&H0C,&HB8,&H11,&H00,&HCD,&H79,&H75
DATA &H05,&h2E,&HC7,&H04,&H01,&H00,&H5E,&H5B,&H58,&HCB

ON ERROR GOTO ERROREND

DIM SHARED NAMELIST(64) AS STRING
DIM SHARED CONTENTLIST(64) AS STRING
DIM SHARED ACTIONLIST(512) AS ActionT

CALL InitTX
CLS:INPUT "请输入文件名：",FILENAME$
IF FILENAME$="" THEN FILENAME$="PPT.TXT"
PRINT "加载中……"
CALL LoadData(FILENAME$)
CALL MainLoop
TX ("KB1,1M3CU1,1")
CLOSE
END

ERROREND:
ERRVAL=ERR
TX ("KB1,1M3CU1,1")
CLOSE
PRINT "Error:";ERRVAL;ERL
END

FUNCTION n$ (A AS INTEGER)
n$ = LTRIM$(RTRIM$(STR$(A)))
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

SUB TX (s AS STRING)
    PRINT #1, CHR$(14); "["; s; "]";
END SUB

SUB ProcessLine(MODE AS STRING, DATATEXT AS STRING)
    SELECT CASE MODE
        CASE ".INIT"
            INITCMD=INITCMD+DATATEXT
        CASE ".CONTENT"
            CONTENTLIST(SLIDECOUNT-1)=CONTENTLIST(SLIDECOUNT-1)+DATATEXT
        CASE ".ACTION"
            ACTIONCOUNT=ACTIONCOUNT+1: I=ACTIONCOUNT-1
            ACTIONLIST(I).SLIDE=SLIDECOUNT-1
            ACTIONLIST(I).TRIGGER=LEFT$(DATATEXT,INSTR(DATATEXT,":")-1)
            TARGET$=RIGHT$(DATATEXT,LEN(DATATEXT)-INSTR(DATATEXT,":"))
            IF INSTR(TARGET$,"EXT$")>0 THEN
                ACTIONLIST(I).EXTERNAL=1
                ACTIONLIST(I).TARGET=RIGHT$(TARGET$,LEN(TARGET$)-4)
            ELSE
                ACTIONLIST(I).EXTERNAL=0
                ACTIONLIST(I).TARGET=TARGET$
            END IF
    END SELECT
END SUB

SUB LoadData(FILENAME AS STRING)
    INITCMD=""
    SLIDECOUNT=0
    ACTIONCOUNT=0
    CURRENTSLIDE=0
    ACTION$=""
    OPEN FILENAME FOR INPUT AS #2
    MODE$=""
    DO
        LINE INPUT #2,DATATEXT$
        DATATEXT$=LTRIM$(RTRIM$(DATATEXT$))
        SELECT CASE DATATEXT$
            CASE ""
            CASE ".SLIDE"
                SLIDECOUNT=SLIDECOUNT+1
                LINE INPUT #2,DATATEXT$
                NAMELIST(SLIDECOUNT-1)=DATATEXT$
                CONTENTLIST(SLIDECOUNT-1)=""
            CASE ".INIT"
                MODE$=DATATEXT$
            CASE ".CONTENT"
                MODE$=DATATEXT$
            CASE ".ACTION"
                MODE$=DATATEXT$
            CASE ELSE
                CALL ProcessLine(MODE$,DATATEXT$)
        END SELECT
    LOOP UNTIL (EOF(2))
    CLOSE #2
END SUB

SUB DisplaySlide(ID as INTEGER)
    CALL TX(CONTENTLIST(ID))
END SUB

FUNCTION GetSlideIdx% (N AS STRING)
    GetSlideIdx%=-1
    FOR I=0 TO SLIDECOUNT-1 STEP 1
        IF N=NAMELIST(I) THEN
            GetSlideIdx%=I: EXIT FUNCTION
        END IF
    NEXT I
END FUNCTION

SUB ProcessTarget(TARGET AS STRING, Ext AS INTEGER)
    IF "NULL"=TARGET THEN EXIT SUB
    IF Ext <> 0 THEN
        ACTION$="LOADPPT"
        FILENAME$=LTRIM$(RTRIM$(TARGET))
    ELSE
        TARGETSLIDE=GetSlideIdx%(RTRIM$(TARGET))
        IF TARGETSLIDE>-1 THEN CURRENTSLIDE=TARGETSLIDE: ACTION$="SWITCHSLIDE"
    END IF
END SUB
SUB ProcessKeyboard(K AS STRING)
    KEY$=K
    IF ACTIONCOUNT>0 THEN
        FOR I=0 TO ACTIONCOUNT-1 STEP 1
            IF ACTIONLIST(I).SLIDE = CURRENTSLIDE THEN
                TRIGGER$=RTRIM$(ACTIONLIST(I).TRIGGER)
                IF TRIGGER$=KEY$ THEN
                    CALL ProcessTarget(ACTIONLIST(I).TARGET, ACTIONLIST(I).EXTERNAL)
                    EXIT SUB
                END IF
            END IF
        NEXT I
        FOR I=0 TO ACTIONCOUNT-1 STEP 1
            IF ACTIONLIST(I).SLIDE=CURRENTSLIDE AND "ANYKEY"=RTRIM$(ACTIONLIST(I).TRIGGER) THEN
                CALL ProcessTarget(ACTIONLIST(I).TARGET, ACTIONLIST(I).EXTERNAL)
                EXIT SUB
            END IF
        NEXT I
    END IF
    SELECT CASE KEY$
        CASE "LEFT"
            IF CURRENTSLIDE>0 THEN CURRENTSLIDE=CURRENTSLIDE-1: ACTION$="SWITCHSLIDE"
        CASE "BACKSPACE"
            IF CURRENTSLIDE>0 THEN CURRENTSLIDE=CURRENTSLIDE-1: ACTION$="SWITCHSLIDE"
        CASE "RIGHT"
            IF CURRENTSLIDE<SLIDECOUNT-1 THEN CURRENTSLIDE=CURRENTSLIDE+1: ACTION$="SWITCHSLIDE"
        CASE "SPACE"
            IF CURRENTSLIDE<SLIDECOUNT-1 THEN CURRENTSLIDE=CURRENTSLIDE+1: ACTION$="SWITCHSLIDE"
    END SELECT
END SUB

SUB MainLoop
    TX(INITCMD)
    CALL DisplaySlide(CURRENTSLIDE)
    DO
        'Handle keyboard action
        K$ = ""
        DO
            K$=INKEY$
        LOOP WHILE K$=""

        SELECT CASE K$
            CASE " "
                K$="SPACE"
            CASE CHR$(27)
                K$="ESC"
            CASE CHR$(9)
                K$="TAB"
            CASE CHR$(0) + "G"
                K$="HOME"
            CASE CHR$(0) + "O"
                K$="END"
            CASE CHR$(0) + "I"
                K$="PAGEUP"
            CASE CHR$(0) + "Q"
                K$="PAGEDOWN"
            CASE CHR$(0) + "H"
                K$="UP"
            CASE CHR$(0) + "P"
                K$="DOWN"
            CASE CHR$(0) + "K"
                K$="LEFT"
            CASE CHR$(0) + "M"
                K$="RIGHT"
            CASE CHR$(0) + "R"
                K$="INSERT"
            CASE CHR$(0) + "S"
                K$="DELETE"
        END SELECT

        SELECT CASE K$
            CASE ""
            CASE "ESC"
                EXIT SUB
            CASE "HOME"
                CURRENTSLIDE=0: ACTION$="SWITCHSLIDE"
            CASE "END"
                CURRENTSLIDE=SLIDECOUNT-1: ACTION$="SWITCHSLIDE"
            CASE "PAGEUP"
                IF CURRENTSLIDE>0 THEN CURRENTSLIDE=CURRENTSLIDE-1: ACTION$="SWITCHSLIDE"
            CASE "PAGEDOWN"
                IF CURRENTSLIDE<SLIDECOUNT-1 THEN CURRENTSLIDE=CURRENTSLIDE+1: ACTION$="SWITCHSLIDE"
            CASE ELSE
                CALL ProcessKeyboard(K$)
        END SELECT

        SELECT CASE ACTION$
            CASE "SWITCHSLIDE"
                ACTION$=""
                CALL DisplaySlide(CURRENTSLIDE)
            CASE "LOADPPT"
                ACTION$=""
                CALL LoadData(FILENAME$)
                CALL DisplaySlide(CURRENTSLIDE)
        END SELECT
        ACTION$=""
    LOOP
END SUB
