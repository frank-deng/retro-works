#include <stdio.h>

#define MAX_IMAGE_WIDTH (640)
#define MAX_IMAGE_WIDTH_COLOR (320)
#define MAX_IMAGE_HEIGHT (200)

static unsigned short mapColor[3][256];

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
} bmp_header_t;
void initMapColor()
{
    unsigned short v, v0, v1, v2;
    unsigned char i;
    for (v = 0; v <= 0xff; v++) {
        v0 = v1 = v2 = 0;
        for (i = 0; i < 8; i++) {
            if ((v & (1 << i)) == 0) {
                continue;
            }
            v0 |= (1 << (i * 2));
            v1 |= (2 << (i * 2));
            v2 |= (3 << (i * 2));
        }
        mapColor[0][v] = (v0 << 8) | ((v0 >> 8) & 0xff);
        mapColor[1][v] = (v1 << 8) | ((v1 >> 8) & 0xff);
        mapColor[2][v] = (v2 << 8) | ((v2 >> 8) & 0xff);
    }
}
void processLine(char *buf, size_t size, unsigned char color)
{
    size_t i;
    if (0 == color) {
        return;
    }
    for (i = size; i > 0; i--) {
        unsigned short val = mapColor[color - 1][buf[i - 1]];
        ((unsigned short *)buf)[i - 1] = val;
    }
}
typedef struct {
    char *arg;
    unsigned char value;
} argMatch_t;
static argMatch_t g_argMatch[] = {
    { "/COLOR1", 1 },
    { "/color1", 1 },
    { "/COLOR2", 2 },
    { "/color2", 2 },
    { "/COLOR3", 3 },
    { "/color3", 3 },
    { NULL, 0 },
};
int parseArgs(int argc, char *argv[], unsigned char *color, char **src, char **dest)
{
    int optind = 1;
    argMatch_t *match = NULL;
    if (argc < 2) {
        return 0;
    }
    *color = 0;

    // Parse color setting
    for (match = g_argMatch; match->arg != NULL; match++) {
        if (0 == strcmp(match->arg, argv[1])) {
            *color = match->value;
            break;
        }
    }

    if (*color != 0) {
        optind = 2;
    }
    if (optind + 1 >= argc) {
        return 0;
    }
    *src = argv[optind];
    *dest = argv[optind + 1];
    return 1;
}
int main(int argc, char *argv[])
{
    unsigned char buf[80];
    unsigned char color = 0;
    char *srcPath = NULL;
    char *destPath = NULL;
    FILE *src = NULL;
    FILE *dest = NULL;
    bmp_header_t bmpHeader;
    unsigned short y, u16val;
    unsigned short rowBytesBmp, rowBytesSrc, rowBytesTarget;

    if (!parseArgs(argc, argv, &color, &srcPath, &destPath)) {
        fputs("Usage: BMP2CGA.EXE [/COLOR1|/COLOR2|/COLOR3] BMP_FILE OUTPUT_FILE\n", stderr);
        return 1;
    }
    initMapColor();

    src = fopen(srcPath, "rb");
    if (NULL == src) {
        fprintf(stderr, "Failed to open source file %s\n", srcPath);
        goto FinallyExit;
    }

    // Checking bmp file
    fread(&bmpHeader, sizeof(bmp_header_t), 1, src);
    if (0x4d42 != bmpHeader.magicNum) {
        fputs("Not a BMP file.\n", stderr);
        goto FinallyExit;
    }
    if (1 != bmpHeader.bpp) {
        fputs("BMP file must be in 1bit monochrome format.\n", stderr);
        goto FinallyExit;
    }
    if (color == 0 && (bmpHeader.width > MAX_IMAGE_WIDTH || bmpHeader.height > MAX_IMAGE_HEIGHT)) {
        fputs("BMP file must be smaller than 640x200 in monochrome mode.\n", stderr);
        goto FinallyExit;
    } else if (color != 0 && (bmpHeader.width > MAX_IMAGE_WIDTH_COLOR || bmpHeader.height > MAX_IMAGE_HEIGHT)) {
        fputs("BMP file must be smaller than 320x200 in color mode.\n", stderr);
        goto FinallyExit;
    }
    rowBytesBmp = ((bmpHeader.width + 0x1f) >> 5) << 2;
    rowBytesSrc = (bmpHeader.width + 0x7) >> 3;
    rowBytesTarget = (color == 0) ? rowBytesSrc : (((bmpHeader.width << 1) + 0x7) >> 3);

    // Prepare target file
    dest = fopen(destPath, "wb");
    if (NULL == dest) {
        fprintf(stderr, "Failed to open target file %s\n", destPath);
        goto FinallyExit;
    }
    fseek(dest, 0, SEEK_SET);

    fwrite("\xfd\x00\xb8\x00\x00", sizeof(char), 5, dest);
    if (bmpHeader.width == (color != 0 ? MAX_IMAGE_WIDTH_COLOR : MAX_IMAGE_WIDTH)
        && bmpHeader.height == MAX_IMAGE_HEIGHT) {
        // Writing to target file (Fullscreen image)
        fwrite("\x00\x40", sizeof(char), 2, dest);
        for (y = 0; y < bmpHeader.height; y += 2) {
            fseek(src, bmpHeader.dataOffset + rowBytesBmp * (bmpHeader.height - 1 - y), SEEK_SET);
            fread(buf, rowBytesSrc, 1, src);
            processLine(buf, rowBytesSrc, color);
            fwrite(buf, rowBytesTarget, 1, dest);
        }
        fseek(dest, 7+8192, SEEK_SET);
        for (y = 1; y < bmpHeader.height; y += 2) {
            fseek(src, bmpHeader.dataOffset + rowBytesBmp * (bmpHeader.height - 1 - y), SEEK_SET);
            fread(buf, rowBytesSrc, 1, src);
            processLine(buf, rowBytesSrc, color);
            fwrite(buf, rowBytesTarget, 1, dest);
        }
        fseek(dest, 7+8192+8192, SEEK_SET);
    } else {
        // Writing to target file (Image fragment for PUT statement)
        u16val = (unsigned short)(rowBytesTarget * bmpHeader.height + 4);
        fwrite(&u16val, sizeof(unsigned short), 1, dest);
        u16val = (unsigned short)(color != 0 ? (bmpHeader.width << 1) : bmpHeader.width);
        fwrite(&u16val, sizeof(unsigned short), 1, dest);
        u16val = (unsigned short)(bmpHeader.height);
        fwrite(&u16val, sizeof(unsigned short), 1, dest);
        for (y = bmpHeader.height; y > 0; y--) {
            fseek(src, bmpHeader.dataOffset + rowBytesBmp * (y - 1), SEEK_SET);
            fread(buf, rowBytesSrc, 1, src);
            processLine(buf, rowBytesSrc, color);
            fwrite(buf, rowBytesTarget, 1, dest);
        }
    }
    fwrite("0x1a", sizeof(char), 1, dest);

FinallyExit:
    if (NULL != src) {
        fclose(src);
    }
    if (NULL != dest) {
        fclose(dest);
    }
    return 0;
}

