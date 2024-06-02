'BSAVE File Format
'
'Bytes Description
'1     ID Flag, always 0xfd
'2     Segment address, little endian, cab be ignored by BLOAD
'2     Offset address, little endian, cab be ignored by BLOAD
'2     Data length, little endian
'n     Data, n=Data length
'1     Tailer flag, always 0x1a
DEFINT A-Z

TYPE BMPHeaderT
    id AS STRING * 2
    size AS LONG
    rr1 AS INTEGER
    rr2 AS INTEGER
    offset AS LONG
    horz AS LONG
    wid AS LONG
    hei AS LONG
    planes AS INTEGER
    bpp AS INTEGER
    pakbyte AS LONG
    imagebytes AS LONG
    xres AS LONG
    yres AS LONG
    colch AS LONG
    ic AS LONG
END TYPE
COMMON hdr AS BMPHeaderT, LBUF AS STRING*160
DIM BITMAP(8194) AS INTEGER

INPUT "BMP file: ",SRC$
INPUT "Output file: ",DST$
OPEN SRC$ FOR BINARY AS #1
GET #1,1,hdr
IF "BM"<>hdr.id THEN PRINT "Invalid BMP File.": GOTO FinallyExit
IF 1<>hdr.bpp THEN PRINT "BMP file must be in 1bit monochrome format.": GOTO FinallyExit
W=hdr.wid: H=hdr.hei
rowBytesBmp=((W+31)\32)*4: rowBytes=(W+7)\8
BITMAP(0)=W: BITMAP(1)=H
DEF SEG=VARSEG(BITMAP(0)): P=VARPTR(BITMAP(0))+4
FOR Y=0 TO H-1
  GET #1,1+hdr.offset+(H-1-Y)*rowBytesBmp,LBUF
  FOR I=0 TO rowBytes-1
    POKE P,ASC(MID$(LBUF,I+1,1)): P=P+1
  NEXT I
NEXT Y

SCREEN 2: LOCATE 1,1,0: CLS
IF DST$<>"" THEN
  DEF SEG=VARSEG(BITMAP(0)): BSAVE DST$,VARPTR(BITMAP(0)),rowBytes*H+4: DEF SEG
  FOR I=0 TO 8193: BITMAP(I)=0: NEXT I
  DEF SEG=VARSEG(BITMAP(0)): BLOAD DST$,VARPTR(BITMAP(0)): DEF SEG
END IF
PUT (0,0),BITMAP,PSET
WHILE INPUT$(1)="": WEND
SCREEN 0: LOCATE 1,1,1: CLS

FinallyExit:
CLOSE
END
