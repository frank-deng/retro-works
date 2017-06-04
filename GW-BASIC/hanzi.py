#!/usr/bin/env python3

import sys, struct;

if (len(sys.argv) < 2):
    sys.stderr.write('Usage: %s chartable X,Y characters\n'%sys.argv[0]);
    exit(1);

with open(sys.argv[1], 'rb') as hzk16:
    x, y = (sys.argv[2].split(','));
    x, y = int(x), int(y);
    count = 0;
    for char in sys.argv[3]:
        gbcode = char.encode('GB2312', 'ignore');
        quwei = (gbcode[0]-0xA1, gbcode[1]-0xA1);
        gdata = [];
        hzk16.seek((quwei[0]*94+quwei[1])*32);
        for n in struct.unpack('H'*16, hzk16.read(32)):
            if (n):
                gdata.append('&H%x'%n);
            else:
                gdata.append('0');
        sys.stdout.write('%d DATA %d,%d,%s\r\n'%(100+count*10, x+count*16, y, ','.join(gdata)));
        count += 1;

