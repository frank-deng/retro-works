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
    unsigned short magicNum;
    unsigned long size;
    unsigned short res;
    unsigned short res2;
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

#define BMP_PALETTE_SIZE (8)
#define BMP_HEADER_SIZE (40)
#define HELP_TEXT "\
Usage: TEXT2BMP.EXE [/f fontasc,fonthzk] [/s width,height] [/c charspace]\n\
                    [/a attr] [/i] /o output.bmp text1 text2 ...\n\
"

static unsigned char bitmapBuf[32768];

int checkEnv()
{
    union REGS regs;
    regs.x.ax = 0xdb00;
    int86(0x2f,&regs,&regs);
    if (regs.x.bx != 0x5450) {
        fputs("Please run UCDOS first.\n", stderr);
        return 1;
    }
    regs.h.ah = 0;
    regs.h.al = 0x1;
    int86(0x79,&regs,&regs);
    if (0 == (regs.x.flags & 0x40)) {
        fputs("Please run RDNFT.COM first.\n", stderr);
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
    param.width = ch <= 0xff ? (width >> 1) : width;
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
void inverseLine(unsigned char *buf, size_t len)
{
    size_t count = (len >> 1), i;
    for (i = 0; i < count; i++) {
        ((uint16_t*)buf)[i] = ~(((uint16_t*)buf)[i]);
    }
    if (len & 1) {
        buf[len - 1] = ~(buf[len - 1]);
    }
}
void getImageSize(charData_t *charData[], short charspc, unsigned short *width, unsigned short *height)
{
    charData_t **pChar = NULL;
    unsigned short imgWidth = 0, imgHeight = 0, x, y;
    // Calculate width and height
    for (pChar = charData; *pChar != NULL; pChar++) {
        unsigned short charWidth = (*pChar)->width;
        if (imgHeight < (*pChar)->height) {
            imgHeight = (*pChar)->height;
        }
        imgWidth += charWidth;
        if (*(pChar + 1) == NULL) {
            continue;
        }
        if (charspc < 0 && -charspc >= charWidth) {
           imgWidth -= charWidth;
        } else {
           imgWidth += charspc;
        }
    }
    *width = imgWidth;
    *height = imgHeight;
}
void writeBMP(FILE *fp, charData_t *charData[], short charspc, unsigned short color)
{
    charData_t **pChar = NULL;
    unsigned short imgWidth = 0, imgHeight = 0, x, y;
    size_t rowBytes = 0;
    bmpHeader_t header;
    getImageSize(charData, charspc, &imgWidth, &imgHeight);

    // Write to bmp
    rowBytes = ((imgWidth + 0x1f) >> 5) << 2;
    header.magicNum = 0x4d42;
    header.size = sizeof(bmpHeader_t) + BMP_PALETTE_SIZE +
        (unsigned long)rowBytes * (unsigned long)imgHeight;
    header.res = header.res2 = 0;
    header.dataOffset = sizeof(bmpHeader_t) + BMP_PALETTE_SIZE;
    header.headerSize = BMP_HEADER_SIZE;
    header.width = imgWidth;
    header.height = imgHeight;
    header.planes = 1;
    header.bpp = 1;
    header.compression = 0;
    header.imageSize = (unsigned long)rowBytes * (unsigned long)imgHeight;
    header.xres = header.yres = 72;
    header.res3 = header.res4 = 0;
    fwrite(&header, sizeof(header), 1, fp);
    fwrite("\0\0\0\0\xff\xff\xff\xff", BMP_PALETTE_SIZE, 1, fp);
    for (y = imgHeight; y > 0; y--) {
        memset(bitmapBuf, 0, rowBytes);
        x = 0;
        for (pChar = charData; *pChar != NULL; pChar++) {
            unsigned short charWidth = (*pChar)->width, charHeight = (*pChar)->height;
            if ((y - 1) < charHeight) {
                drawPixels(bitmapBuf, x, (*pChar)->data + (y - 1) * (*pChar)->rowSize, (*pChar)->rowSize);
            }
            x += charWidth;
            if (*(pChar + 1) == NULL) {
                continue;
            }
            if (charspc < 0 && -charspc >= charWidth) {
               x -= charWidth;
            } else {
               x += charspc;
		    }
		}
        if (color & 1) {
            inverseLine(bitmapBuf, rowBytes);
        }
        fwrite(bitmapBuf, rowBytes, 1, fp);
    }
}

typedef enum {
    DEFAULT,
    DISPLAY_HELP,
    SET_FONT,
    SET_SIZE,
    SET_SPACE,
    SET_ATTR,
    SET_INVERSE,
    SET_OUTPUT_FILE
} getopt_action_t;
typedef struct {
    const char *arg;
    const char *arg2;
    unsigned char param;
    getopt_action_t action;
} getopt_table_t;
typedef struct {
    char *outFile;
    unsigned short ascfont;
    unsigned short hzkfont;
    unsigned short width;
    unsigned short height;
    unsigned short attr;
    unsigned short space;
    unsigned short color;
} getopt_t;
static getopt_table_t g_getoptTable[] = {
    { "/o", "/O", 1,  SET_OUTPUT_FILE },
    { "/f", "/F", 1,  SET_FONT },
    { "/s", "/S", 1,  SET_SIZE },
    { "/c", "/C", 1,  SET_SPACE },
    { "/a", "/A", 1,  SET_ATTR },
    { "/i", "/I", 0,  SET_INVERSE },
    { "/h", "/H", 0,  DISPLAY_HELP },
    { NULL, NULL, 0, DEFAULT}
};
int processArgs(int argc, char *argv[], getopt_t *opts, int *optind)
{
    getopt_table_t *item = NULL;
    char *paramStr = NULL;
    int i, j;
    opts->outFile = NULL;
    opts->ascfont = opts->hzkfont = 0;
    opts->width = opts->height = 16;
    opts->attr = 1;
    opts->space = 0;
    opts->color = 0;
    for (i = 1; i < argc; i++) {
        for (item = g_getoptTable; item->arg != NULL; item++) {
            if (!strcmp(argv[i], item->arg) || !strcmp(argv[i], item->arg2)) {
                break;
            }
        }
        if (NULL == item->arg) {
            break;
        }
        paramStr = NULL;
        if (item->param) {
            if (i + 1 >= argc) {
                return 0;
            }
            i++;
            paramStr = argv[i];
        }
        switch (item->action) {
            case DISPLAY_HELP:
                return 0;
            break;
            case SET_INVERSE:
                opts->color = 1;
            break;
            case SET_OUTPUT_FILE:
                opts->outFile = paramStr;
            break;
            case SET_FONT:
                sscanf(paramStr, "%u,%u", &(opts->ascfont), &(opts->hzkfont));
            break;
            case SET_SIZE:
                sscanf(paramStr, "%u,%u", &(opts->width), &(opts->height));
            break;
            case SET_SPACE:
                opts->space = atoi(paramStr);
            break;
            case SET_ATTR:
                opts->attr = atoi(paramStr);
            break;
        }
    }
    if (i >= argc || NULL == opts->outFile) {
        return 0;
    }
    *optind = i;
    return 1;
}
int main(int argc, char *argv[])
{
    getopt_t opts;
    int optind = 1;
    charData_t *charData[512];
    size_t charDataLen = 0;
    int i;
    char *p;
    FILE *target = NULL;

    if (!processArgs(argc, argv, &opts, &optind)) {
        fputs(HELP_TEXT, stderr);
        return 1;
    }
    if (checkEnv() != 0) {
        return 2;
    }
    target = fopen(opts.outFile, "wb");
    if (NULL == target) {
        fputs("Failed to open target file.\n", stderr);
        return 3;
    }

    // Get bitmap for each character
    for (i = optind; i < argc; i++) {
        if (i != optind) {
            charData[charDataLen] = getCharBitmap(' ', opts.ascfont, opts.hzkfont,
                 opts.width, opts.height, opts.attr);
            charDataLen++;
        }
        for (p = argv[i]; *p != '\0'; p++) {
             unsigned short chData = *p;
             if (chData > 0x7f && *(p + 1) != '\0') {
                 chData <<= 8;
                 p++;
                 chData |= *p;
             }
             charData[charDataLen] = getCharBitmap(chData, opts.ascfont, opts.hzkfont,
                 opts.width, opts.height, opts.attr);
             charDataLen++;
         }
    }
    charData[charDataLen] = NULL;
    writeBMP(target, charData, opts.space, opts.color);

    // Clean up
    for (i = 0; i < charDataLen; i++) {
        free(charData[i]);
    }
    fclose(target);
    return 0;
}