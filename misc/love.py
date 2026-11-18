"""把图片转成 8bpp 256 色索引图, 前 16 色保留给系统 (VGA 默认 16 色).

    im  = imgproc("BG.JPG")      # P 模式, 索引 16..255, 可直接 ImageDraw 绘图
    imgsave(im, "BG.BMP")

    # 用点阵字体写字, 无抗锯齿 (fill 给调色板索引)
    f = open_gbk_font("SKAITI.TTF", 16)
    d = ImageDraw.Draw(im)
    d.fontmode = "1"
    d.text((100, 100), gb("石头"), font=f, fill=15)

调色板布局: 0..15 标准 VGA 16 色(图像不使用, 留给 UI/文字/光标) + 16..255 自适应色.
抖动为 Floyd-Steinberg, 可选目标里不含 0..15.
"""
import io
import math
import struct

from PIL import Image, ImageOps, ImageDraw, ImageFont

STD16 = [
    (0, 0, 0), (0, 0, 170), (0, 170, 0), (0, 170, 170),
    (170, 0, 0), (170, 0, 170), (170, 85, 0), (170, 170, 170),
    (85, 85, 85), (85, 85, 255), (85, 255, 85), (85, 255, 255),
    (255, 85, 85), (255, 85, 255), (255, 255, 85), (255, 255, 255),
]
RESERVED = len(STD16)


def imgproc(src, size=(640, 480), ncolors=240, kmeans=8,
            method=Image.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG, sort="luma"):
    """读入 src 并返回 P 模式 256 色图像, 尺寸 size=(W, H).

    sort: 自适应色在 16..255 中的排序方式, "luma"(按亮度) / "freq"(按频率) / "none".
    """
    im = ImageOps.exif_transpose(Image.open(src))
    im = im.convert("RGB").resize(size, Image.LANCZOS)

    # 量化到 ncolors 色: 索引恰好落在 0..ncolors-1, 禁区物理上不存在
    q = im.quantize(colors=ncolors, method=method, kmeans=kmeans, dither=dither)
    pal = q.getpalette()[:ncolors * 3]
    colors = [tuple(pal[i * 3:i * 3 + 3]) for i in range(ncolors)]

    if sort == "luma":
        order = sorted(range(ncolors),
                       key=lambda i: (299 * colors[i][0] + 587 * colors[i][1]
                                      + 114 * colors[i][2], i))
    elif sort == "freq":
        hist = q.histogram()
        order = sorted(range(ncolors), key=lambda i: (-hist[i], i))
    else:
        order = list(range(ncolors))

    # 旧索引 -> 最终索引(含 +RESERVED 平移)
    lut = [RESERVED] * 256
    for pos, old in enumerate(order):
        lut[old] = RESERVED + pos

    out = Image.frombytes("P", size, q.tobytes().translate(bytes(lut)))
    palette = [c for color in STD16 for c in color]
    for old in order:
        palette.extend(colors[old])
    out.putpalette(palette + [0] * (768 - len(palette)))
    return out


def open_gbk_font(path, size):
    """打开 GBK 码位的 TTF, 返回指定字号的字体对象.

    该字体 cmap 的编码记录是 (3,3)=GBK, FreeType 不认, 直接 truetype()
    取字模会全部落到 .notdef(空轮廓). 这里只把 platEncID 3 改成 1
    (Unicode BMP), 其余字节不动, 经 BytesIO 打开, 不改磁盘上的原文件.
    文字需先用 gb() 转成 GBK 码位再交给 ImageDraw.
    """
    raw = bytearray(open(path, "rb").read())
    num, = struct.unpack(">H", raw[4:6])
    for i in range(num):
        p = 12 + 16 * i
        if raw[p:p + 4] == b"cmap":
            cmap = struct.unpack(">I", raw[p + 8:p + 12])[0]
            break
    else:
        raise ValueError("%s: no cmap table" % path)
    struct.pack_into(">H", raw, cmap + 6, 1)
    return ImageFont.truetype(io.BytesIO(bytes(raw)), size)


def gb(s):
    """把文本转成该字体里的 GBK 码位串, 每个字对应一个 chr().

    落在 0xD800..0xDFFF (GB2312 区位 56..63 的三级汉字) 的字无法用 chr()
    表达, FreeType 会当成空字形, 这些字需要别的手段.
    """
    b = s.encode("gbk")
    out, i = [], 0
    while i < len(b):
        if b[i] < 0x80:
            out.append(chr(b[i]))
            i += 1
        else:
            out.append(chr(b[i] << 8 | b[i + 1]))
            i += 2
    return "".join(out)


if __name__=='__main__':
    im = imgproc('love.jpg')
    d = ImageDraw.Draw(im)
    d.fontmode = "1"                        # 无抗锯齿

    FONTSIZE, X0, Y0 = 98, 10, 40           # LOVE2.BAS: FONTSIZE=98:X0=10:Y0=40
    RIGHTX = 638 - X0 - FONTSIZE * 2        # 右侧"春婷"的起点, 右边缘对齐 638-X0
    font = open_gbk_font("SKAITI.TTF", FONTSIZE)

    # 主色 11(亮青) + 描边 3(青), 八向各偏移 1 像素
    for s, x in (("石头", X0), ("春婷", RIGHTX)):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    d.text((x + dx, Y0 + dy), gb(s), font=font, fill=3)
        d.text((x, Y0), gb(s), font=font, fill=11)

    # 爱心: 上半两个半径 50 的半圆 + 下半按余弦收尖, 内部色 13, 轮廓色 5
    HEARTX, HEARTY, HEARTW, HEARTH = 320, 10, 50, 150
    for cx in (HEARTX - HEARTW, HEARTX + HEARTW):
        cy = HEARTY + HEARTW
        box = (cx - HEARTW, cy - HEARTW, cx + HEARTW, cy + HEARTW)
        d.pieslice(box, 180, 360, fill=13)      # 半圆盘(心形的两个凸起)
        d.arc(box, 180, 360, fill=5)            # 再压一条 1px 弧线做轮廓
    for i in range(1, HEARTH + 1):
        x = int(HEARTW * 2 * math.cos(math.pi * i / 2 / HEARTH) + .5)
        y = HEARTY + HEARTW + i
        d.line([(HEARTX - x, y), (HEARTX + x, y)], fill=13)
        d.point((HEARTX - x, y), fill=5)
        d.point((HEARTX + x, y), fill=5)

    im.save('love.bmp', format="BMP")
