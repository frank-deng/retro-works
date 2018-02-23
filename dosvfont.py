#!/usr/bin/env python3

import struct, sys, traceback;

if (len(sys.argv) < 4):
    print("Usage: %s ANK16.FNT KANJI16.FNT FONT.BMP"%sys.argv[0]);
    exit(1);

ank16 = None;
with open(sys.argv[1], 'rb') as f:
    data = f.read();
    ank16 = [data[i:i+16] for i in range(0, 256*16, 16)];

kanji16 = None;
charTable = {};
for row in range(0xa1, 0xff):
    for col in range(0xa1, 0xff):
        code = "%02x%02x"%(row & 0x7F, col & 0x7F);
        char = struct.pack('BB', row, col).decode('euc-jp', errors='ignore');
        sjis = char.encode('shift-jis', errors='ignore');
        if (len(char) > 0 and len(sjis) > 0):
            charTable[code] = {
                'eucjp': (row & 0x7f, col & 0x7f),
                'utf8': char,
                'sjis': (sjis[0], sjis[1]),
                'pixel': None,
            };

with open(sys.argv[2], 'rb') as f:
    for k in sorted(charTable.keys()):
        ch = charTable[k];
        row, col = ch['sjis'];
        if row <= 0x84:
            f.seek(512 + ((row - 0x81) * 189 + (col - 0x40)) * 32);
        else:
            f.seek(512 + ((row - 0x81) * 189 + (col - 0x40) - 378) * 32);
        pixelData = f.read(32);
        if pixelData != b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0':
            ch['pixel'] = pixelData;

def writeBMP(f, metadata, x, y, data):
    offset = metadata[2];
    width = metadata[4];
    height = metadata[5];
    if (x < 0 or y < 0):
        print("Error pos: ",x,y);
        return;
    f.seek(offset + (((height - y - 1) * width) >> 3) + x);
    f.write(data);

def writeChar(f, metadata, x, y, data):
    for i in range(16):
        d = data[i*2];
        writeBMP(f, metadata, x*2, y*16+i, struct.pack('B', (~d & 0xFF)));
        d = data[i*2 + 1];
        writeBMP(f, metadata, x*2+1, y*16+i, struct.pack('B', (~d & 0xFF)));

f = open(sys.argv[3], 'r+b');
try:
    metadata = struct.unpack('<HLxxxxLLLLHHLLLLLL', f.read(14+40));
    for ch, ank in enumerate(ank16):
        if not ((ch >= 0x20 and ch <= 0x7e) or (ch >= 0xA1 and ch <= 0xdf)):
            continue;
        for i, d in enumerate(ank):
            writeBMP(f, metadata, ch, i, struct.pack('B', (~d & 0xFF)));
    for k in sorted(charTable.keys()):
        ch = charTable[k];
        row, col = ch['eucjp'];
        if (None != ch['pixel'] and len(ch['pixel']) == 32):
            writeChar(f, metadata, row - 0x20, col, ch['pixel']);
except Exception as e:
    traceback.print_exc();
finally:
    f.close();

'''
def printPixels(data):
    if (None == data):
        return;
    pixels = '';
    for i, row in enumerate(data):
        for j in range(8):
            if (row & (1 << (7-j))):
                pixels += '#';
            else:
                pixels += '.';
        if (i & 1):
            pixels += '\n';
    print(pixels);
    print('\n');
if (len(sys.argv) > 1 and sys.argv[1] == 'l'):
    with open('KANJI16.FNT', 'rb') as f:
        for i in range(8192):
            f.seek(512 + i * 32);
            print("%04x %d"%(i, i));
            printPixels(f.read(32));
    exit();
for k in sorted(charTable.keys()):
    ch = charTable[k];
    print(k, "%02x%02x"%ch['sjis'], ch['utf8']);
    printPixels(ch['pixel']);
'''

