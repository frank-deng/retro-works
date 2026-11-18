/* love.c -- 在 VESA 640x480x256 (模式 101h) 下显示 LOVE.BMP, 按任意键返回 DOS
 *
 * 构建 (Open Watcom, 16 位实模式 DOS):
 *   wcl -0 -ml -bt=dos -l=dos -fe=love.exe love.c
 */
#include <stdio.h>
#include <string.h>
#include <conio.h>
#include <i86.h>

#define BMP_FILE   "LOVE.BMP"
#define VBE_MODE   0x0101       /* 640x480x8bpp, VBE 1.2 起的标准模式号 */
#define TEXT_MODE  0x0003
#define VGA_SEG    0xA000u      /* 窗口 A 段址 (VBE 模式信息里通常也是这个) */

static unsigned char mode_info[512];
static unsigned char linebuf[640];
static unsigned char palbuf[1024];

static unsigned int cur_bank = 0xFFFFu;  /* 当前已切换的窗口号, 0xFFFF=未知 */

static unsigned int get16(const unsigned char *p)
{
    return (unsigned int)p[0] | ((unsigned int)p[1] << 8);
}

static unsigned long get32(const unsigned char *p)
{
    return (unsigned long)get16(p) | ((unsigned long)get16(p + 2) << 16);
}

static int vbe_get_mode_info(unsigned int mode)
{
    union REGS r;
    struct SREGS s;

    r.x.ax = 0x4F01;
    r.x.cx = mode;
    s.es = FP_SEG(mode_info);
    r.x.di = FP_OFF(mode_info);
    int86x(0x10, &r, &r, &s);
    return r.x.ax == 0x004F;
}

static int vbe_set_mode(unsigned int mode)
{
    union REGS r;

    r.x.ax = 0x4F02;
    r.x.bx = mode;
    int86(0x10, &r, &r);
    return r.x.ax == 0x004F;
}

static void vbe_set_bank(unsigned int bank)
{
    union REGS r;

    r.x.ax = 0x4F05;
    r.x.bx = 0;                 /* 窗口 A */
    r.x.dx = bank;
    int86(0x10, &r, &r);
}

/* BMP 调色板是 BGR0, VGA DAC 只要 6 位/分量 */
static void set_palette(void)
{
    int i;

    outp(0x3C8, 0);
    for (i = 0; i < 256; i++) {
        outp(0x3C9, palbuf[i * 4 + 2] >> 2);    /* R */
        outp(0x3C9, palbuf[i * 4 + 1] >> 2);    /* G */
        outp(0x3C9, palbuf[i * 4 + 0] >> 2);    /* B */
    }
}

/* 把 n 字节送到显存线性地址 ofs, 按 64K 粒度换 bank */
static void put_line(const unsigned char *src, unsigned long ofs, unsigned int n)
{
    unsigned int bank, off, chunk;
    unsigned long space;
    unsigned char __far *vid;

    bank = (unsigned int)(ofs >> 16);
    off  = (unsigned int)(ofs & 0xFFFFu);
    if (bank != cur_bank) {
        vbe_set_bank(bank);
        cur_bank = bank;
    }
    while (n) {
        space = 0x10000UL - (unsigned long)off;     /* 窗口还能放多少字节 */
        chunk = (space > (unsigned long)n) ? n : (unsigned int)space;
        vid = (unsigned char __far *)MK_FP(VGA_SEG, off);
        memcpy(vid, src, chunk);
        n -= chunk;
        src += chunk;
        if (n) {                                    /* 越过窗口边界, 换下一段 */
            vbe_set_bank(++bank);
            cur_bank = bank;
            off = 0;
        }
    }
}

int main(void)
{
    FILE *fp;
    unsigned char hdr[54];
    unsigned int width, height, bpp, scanline, rowbytes, pad;
    unsigned long data_ofs;
    unsigned int y, sy;
    int h, bottom_up, err = 0;

    if ((fp = fopen(BMP_FILE, "rb")) == NULL) {
        printf("Cannot open %s\n", BMP_FILE);
        return 1;
    }
    if (fread(hdr, 1, 54, fp) != 54 || hdr[0] != 'B' || hdr[1] != 'M') {
        printf("%s is not a BMP file\n", BMP_FILE);
        fclose(fp);
        return 1;
    }

    data_ofs = get32(hdr + 10);         /* bfOffBits */
    width    = get16(hdr + 18);         /* biWidth  */
    h        = (int)get16(hdr + 22);    /* biHeight, 负数表示 top-down */
    bpp      = get16(hdr + 28);         /* biBitCount */
    bottom_up = (h > 0);
    height   = (unsigned int)(bottom_up ? h : -h);

    if (width != 640 || height != 480 || bpp != 8 || get32(hdr + 30) != 0) {
        printf("%s must be 640x480x256 uncompressed\n", BMP_FILE);
        fclose(fp);
        return 1;
    }

    if (fseek(fp, 54L, SEEK_SET) != 0 || fread(palbuf, 1, 1024, fp) != 1024) {
        printf("Cannot read palette\n");
        fclose(fp);
        return 1;
    }

    if (!vbe_get_mode_info(VBE_MODE)) {
        printf("VESA VBE mode 101h is not available\n");
        fclose(fp);
        return 1;
    }
    scanline = get16(mode_info + 0x12);     /* BytesPerScanLine */
    if (scanline < width)
        scanline = width;

    if (!vbe_set_mode(VBE_MODE)) {
        printf("Cannot set VESA mode 101h\n");
        fclose(fp);
        return 1;
    }

    set_palette();

    rowbytes = ((width * bpp + 31u) / 32u) * 4u;    /* BMP 行 4 字节对齐 */
    pad = rowbytes - width;

    fseek(fp, (long)data_ofs, SEEK_SET);
    for (y = 0; y < height; y++) {
        if (fread(linebuf, 1, width, fp) != width) {
            err = 1;
            break;
        }
        if (pad)
            fseek(fp, (long)pad, SEEK_CUR);
        sy = bottom_up ? (height - 1 - y) : y;
        put_line(linebuf, (unsigned long)sy * scanline, width);
    }

    if (!err)
        getch();                    /* 按任意键返回 DOS */

    fclose(fp);
    vbe_set_mode(TEXT_MODE);

    if (err)
        printf("Error reading %s\n", BMP_FILE);

    return err;
}
