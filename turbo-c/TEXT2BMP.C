#include <dos.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <malloc.h>

typedef unsigned char uint8_t;
typedef unsigned short uint16_t;
typedef struct {
    unsigned short width;
    unsigned short height;
    size_t rowSize;
    unsigned char *data;
} charData_t;
typedef struct {
    unsigned short lineHeight;
    unsigned short indent;
    unsigned char ascFont;
    unsigned char hzkFont;
    unsigned short fontWidth;
    unsigned short fontHeight;
    unsigned short fontAttr;
    short charSpace;
    charData_t *data;
} rowData_t;
typedef struct {
    unsigned short magicNum;
    unsigned long size;
    unsigned long res;
    unsigned long dataOffset;
    unsigned long headerSize;
    long width;
    long height;
    unsigned short planes;
    unsigned short bpp;
    unsigned long compression;
    unsigned long imageSize;
    long xres;
    long yres;
    unsigned long res3;
    unsigned long res4;
} bmpHeader_t;

static uint8_t bitmapBuf[32768];

int checkEnv()
{
    union REGS regs;
    regs.h.ah = 0;
	regs.h.al = 0x1;
	int86(0x79,&regs,&regs);
	if (0 == regs.x.flags & 0x40) {
		return 1;
	}
    return 0;
}
charData_t* getCharBitmap(unsigned short ch, unsigned char fontAsc, unsigned char fontHzk,
    unsigned short width, unsigned short height, unsigned short attr)
{
    union REGS regs;
	struct SREGS sregs;
    size_t rowSize, dataSize;
    charData_t *res = NULL;
    struct Int7eParam_s{
        unsigned short ch;
        unsigned short font;
        unsigned short width;
        unsigned short height;
        unsigned short top;
        unsigned short bottom;
        unsigned short attr;
        unsigned short buflen;
    } param;
    param.ch = ch;
    param.font = ch <= 0xff ? fontAsc : fontHzk,
    param.width = width;
    param.height = height;
    param.top = 0;
    param.bottom = height - 1;
    param.attr = attr;
    param.buflen = sizeof(bitmapBuf);
    regs.x.si = FP_OFF(&param);
	regs.x.di = FP_OFF(bitmapBuf);
	sregs.ds = FP_SEG(&param);
	sregs.es = FP_SEG(bitmapBuf);
    int86x(0x7e, &regs, &regs, &sregs);
    rowSize = (param.width + 0x7) >> 3;
    dataSize = rowSize * param.height;
    res = (charData_t*)malloc(sizeof(charData_t) + dataSize);
    res->width = param.width;
    res->height = param.height;
    res->rowSize = rowSize;
    res->data = ((uint8_t*)res) + sizeof(charData_t);
    memcpy(res->data, bitmapBuf, dataSize);
    return res;
}
void drawPixels(unsigned char *dest, unsigned short pos,
    unsigned char *src, unsigned short length)
{
    unsigned short i, bias = pos & 0x7;
    unsigned char val, *pSrc = src, *pDest = dest + (pos >> 3);
    if (bias == 0) {
        while (length) {
            *pDest |= *pSrc;
            pSrc++;
            pDest++;
            length--;
        }
        return;
    }
    *pDest |= (*pSrc >> bias);
    pDest++;
    length--;
    while (length) {
        val = *pSrc << (8 - bias);
        pSrc++;
        val |= *pSrc >> bias;
        *pDest |= val;
        pDest++;
        length--;
    }
    *pDest |= (*pSrc << (8 - bias));
}
void writeBMP(FILE *fp, charData_t *charData, short charspc)
{
    charData_t *pChar = NULL;
    unsigned short imgWidth = 0, imgHeight = 0, x, y;
    size_t rowBytes = 0;
    unsigned char *bmpData = NULL, *pBmp = NULL;
    bmpHeader_t header;
    for (pChar = charData; pChar != NULL; pChar++) {
        if (imgHeight < pChar->height) {
            imgHeight = pChar->height;
        }
        imgWidth += width;
        if (pChar != charData) {
            imgWidth += charspc;
        }
    }
    rowBytes = ((imgWidth + 0x1f) >> 5) << 2;
    bmpData = (unsigned char *)calloc(rowBytes, imgHeight);
    printf("%d %d\n", imgWidth, imgHeight);
    x = 0;
    for (pChar = charData; pChar != NULL; pChar++) {
        for (y = 0; y < pChar->height; y++) {
            drawPixels(bmpData + y * rowBytes, x,
                pChar->data + y * pChar->rowSize, pChar->rowSize);
        }
        x += width;
        if (pChar != charData) {
            x += charspc;
        }
    }
}
int main(int argc, char *argv[])
{
    unsigned char ascfont, hzkfont;
    unsigned short width, height;
    short charspc;
    charData_t *charData[512];
    size_t charDataLen = 0;
    int i;
    char *p;
    FILE *target = NULL;

    if (argc < 4) {
        fputs("Usage: TEXT2BMP.EXE ascfont,hzkfont,width,height,space text bmpfile.bmp\n", stderr);
        return 1;
    }
    if (checkEnv() != 0) {
        fputs("Please run RDNFT.COM first.\n", stderr);
        return 2;
    }
    if (5 != sscanf(argv[1], "%u,%u,%u,%u,%d", &ascfont, &hzkfont, &width, &height, &charspc)) {
        fputs("Failed to specify font format.\n", stderr);
        return 3;
    }
    target = fopen(argv[3], "wb");
    if (NULL == target) {
        fputs("Failed to open target file.\n", stderr);
        return 4;
    }

    // Get bitmap for each character
    for (p = argv[2]; *p != '\0'; p++) {
         unsigned short chData = *p;
         if (chData > 0x7f) {
             chData <<= 8;
             p++;
             chData |= *p;
         }
         charData[charDataLen] = getCharBitmap(chData, ascfont, hzkfont, width, height, 1);
         charDataLen++;
    }
    charData[charDataLen] = NULL;
    writeBMP(fp, charData, charspc);
    fclose(target);
    return 0;
}
