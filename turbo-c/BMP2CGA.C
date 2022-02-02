#include <stdio.h>

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
int main(int argc, char *argv[])
{
    unsigned char buf[80];
    FILE *src = NULL;
    FILE *dest = NULL;
    bmp_header_t bmpHeader;
    unsigned short y;

    if (argc < 3) {
        fputs("Usage: bmp2cga.exe BMP_FILE OUTPUT_FILE\n", stderr);
        return 1;
    }

    src = fopen(argv[1], "rb");
    if (NULL == src) {
        fprintf(stderr, "Failed to open source file %s\n", argv[1]);
        return 1;
    }

    // Checking bmp file
	fread(&bmpHeader, sizeof(bmp_header_t), 1, src);
    if (0x4d42 != bmpHeader.magicNum) {
        fputs("Not a BMP file.\n", stderr);
        return 1;
    }
    if (1 != bmpHeader.planes){
        fputs("Invalid BMP file.\n", stderr);
        return 1;
    }
		if (640 != bmpHeader.width || 200 != bmpHeader.height || 1 != bmpHeader.bpp) {
        fputs("BMP file must be in 640x200 1bit monochrome format.\n", stderr);
        return 1;
    }

    // Writing to target file
    dest = fopen(argv[2], "wb");
    if (NULL == dest) {
        fprintf(stderr, "Failed to open target file %s\n", argv[2]);
        return 1;
    }
    fseek(dest, 0, SEEK_SET);
    fwrite("\xfd\x00\xb8\x00\x00\x00\x40", sizeof(char), 7, dest);
    for (y = 0; y < bmpHeader.height; y += 2) {
        fseek(src, bmpHeader.dataOffset + 80 * (199 - y), SEEK_SET);
        fread(buf, sizeof(buf), 1, src);
        fwrite(buf, sizeof(buf), 1, dest);
    }
    fseek(dest, 7+8000+192, SEEK_SET);
    for (y = 1; y < bmpHeader.height; y += 2) {
        fseek(src, bmpHeader.dataOffset + 80 * (199 - y), SEEK_SET);
        fread(buf, sizeof(buf), 1, src);
        fwrite(buf, sizeof(buf), 1, dest);
    }
    fseek(dest, 7+8000+192+8000+192, SEEK_SET);
    fwrite("0x1a", sizeof(char), 1, dest);

    // Close files
    fclose(src);
    fclose(dest);
    return 0;
}
