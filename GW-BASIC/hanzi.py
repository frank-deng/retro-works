#!/usr/bin/env python3

import sys, struct, argparse;

class PositionParser(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            x,y = values.split(',');
            x,y = int(x),int(y);
        except Exception as e:
            parser.error('Invalid position format.');
        setattr(namespace, self.dest, (x,y));

argParser = argparse.ArgumentParser();
argParser.add_argument(
    '--font',
    '-f',
    help='Specify font file.',
    default='HZK16.FON'
);
argParser.add_argument(
    'position',
    action=PositionParser,
    help='Specify position to display text.'
);
argParser.add_argument(
    'text',
    help='Chinese text to display.'
);
args = argParser.parse_args();

with open(args.font, 'rb') as hzk16:
    x, y = args.position;
    count = 0;
    for char in args.text:
        gbcode = char.encode('GB2312', 'ignore');
        if (len(gbcode) != 2):
            continue;
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

