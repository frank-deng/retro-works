#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#define BMP_PALETTE_SIZE (8)
#define BMP_HEADER_SIZE (40)

typedef struct {
    uint32_t size;
    uint32_t res;
    uint32_t dataOffset;
    uint32_t headerSize;
    uint32_t width;
    uint32_t height;
    uint16_t planes;
    uint16_t bpp;
    uint32_t compression;
    uint32_t imageSize;
    uint32_t xres;
    uint32_t yres;
    uint32_t res3;
    uint32_t res4;
} bmpHeader_t;

#define HELP_TEXT "\
Usage: carpet level output.bmp\n\
       (level should between 3-7)\n\
"

bool parseArgs(int argc, char *argv[], uint8_t *level, char **path)
{
    if (argc < 3) {
        goto Error;
    }
    *level = atoi(argv[1]);
    if (*level < 3 || *level > 7) {
        goto Error;
    }
    *path = argv[2];
    return true;
Error:
    fputs(HELP_TEXT, stderr);
    return false;
}
static inline uint16_t getSize(uint8_t level)
{
    uint16_t result = 1;
    while (level > 0) {
        result *= 3;
        level--;
    }
    return result;
}
bool drawPoint(uint16_t x, uint16_t y)
{
    while (x > 0 && y > 0) {
        if (1 == (x % 3) && 1 == (y % 3)) {
            return false;
        }
        x /= 3;
        y /= 3;
    }
    return true;
}
void drawCarpet(uint16_t size, FILE *fp)
{
    uint8_t buf[280];
    uint16_t x, y;
    size_t rowBytes = ((size + 0x1f) >> 5) << 2;
    bmpHeader_t header;

    header.size = 2 + sizeof(bmpHeader_t) + BMP_PALETTE_SIZE +
        (uint32_t)rowBytes * (uint32_t)size;
    header.res = 0;
    header.dataOffset = 2 + sizeof(bmpHeader_t) + BMP_PALETTE_SIZE;
    header.headerSize = BMP_HEADER_SIZE;
    header.width = size;
    header.height = size;
    header.planes = 1;
    header.bpp = 1;
    header.compression = 0;
    header.imageSize = (uint32_t)rowBytes * (uint32_t)size;
    header.xres = header.yres = 72;
    header.res3 = header.res4 = 0;
    fwrite("BM", 2, 1, fp);
    fwrite(&header, sizeof(header), 1, fp);
    fwrite("\0\0\0\0\xff\xff\xff\xff", BMP_PALETTE_SIZE, 1, fp);
    for (y = 0; y <= size; y++) {
        for (x = 0; x <= size; x++) {
            if (drawPoint(x, y)) {
                buf[x >> 3] |= (1 << (7 - (x & 0x7)));
            } else {
                buf[x >> 3] &= ~(1 << (7 - (x & 0x7)));
            }
        }
        fwrite(buf, sizeof(uint8_t), rowBytes, fp);
    }
}
int main(int argc, char *argv[])
{
    uint8_t level = 0;
    char *path = NULL;
    FILE *fp = NULL;
    if (!parseArgs(argc, argv, &level, &path)) {
        return 1;
    }
    fp = fopen(path, "wb");
    if (NULL == fp) {
        fprintf(stderr, "Unable to open output file: %s\n", path);
        return 2;
    }
    drawCarpet(getSize(level), fp);
    fclose(fp);
    return 0;
}