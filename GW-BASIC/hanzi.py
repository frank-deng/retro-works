#!/usr/bin/env python3

import sys;

if (len(sys.argv) < 2):
    sys.stderr.write('Usage: %s X,Y characters\n'%sys.argv[0]);
    exit(1);

convtab = [
    0x0, 0x3, 0xC, 0xF,
    0x30, 0x33, 0x3C, 0x3F,
    0xC0, 0xC3, 0xCC, 0xCF,
    0xF0, 0xF3, 0xFC, 0xFF,
]
byte2graph = lambda b:convtab[b&0x0F] << 8 | convtab[(b>>4)&0x0F];

count = 0;
x, y = (sys.argv[1].split(','));
x, y = int(x), int(y);
for char in sys.argv[2]:
    gbcode = char.encode('GB2312', 'ignore');
    quwei = (gbcode[0]-0xA1, gbcode[1]-0xA1);
    gdata = [];
    with open('HZK16', 'rb') as hzk16:
        hzk16.seek((quwei[0]*94+quwei[1])*32);
        for byte in hzk16.read(32):
            if (byte):
                gdata.append('&H%x'%byte);
            else:
                gdata.append('0');
    sys.stdout.write('%d DATA %d,%d,%s\r\n'%(100+count, x+count*16, y, ','.join(gdata)));
    count += 1;

