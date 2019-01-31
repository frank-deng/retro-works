#!/usr/bin/env python3

import sys, struct, argparse;

class TextDispParser(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        text_all = getattr(namespace, self.dest);
        for v in values:
            try:
                pos,text = v.split(':');
                x,y = pos.split(',');
                x,y = int(x),int(y);
                text_all.append({'pos':(x,y), 'text':text});
            except Exception as e:
                print(str(e));
        setattr(namespace, self.dest, text_all);

argParser = argparse.ArgumentParser();
argParser.add_argument(
    '--font',
    '-f',
    help='Specify font file.',
    default='HZK16.FON'
);
argParser.add_argument(
    '-o',
    metavar='output',
    help='Output file.'
);
argParser.add_argument(
    '--mode',
    '-m',
    metavar='mode',
    help='Output file.'
);
argParser.add_argument(
    'textdisp',
    metavar='X,Y:Text',
    nargs='+',
    action=TextDispParser,
    help='Chinese text to display, in the format of X,Y:TEXT.',
    default=[]
);

class TextDataMaker:
    def __init__(self, font, output = sys.stdout):
        self.__font = open(font, 'rb');
        self.__lineSpace = 10;
        self.__line = 110;
        self.__out = output;
    
    def __enter__(self):
        return self;
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.__font.close();

    def __nextLine(self):
        self.__line += self.__lineSpace;

    def getFontData(self,char):
        gbcode = char.encode('GB2312', 'ignore');
        if (len(gbcode) != 2):
            return None;
        qu,wei = gbcode[0]-0xA1, gbcode[1]-0xA1;
        self.__font.seek((qu*94+wei)*32);
        return struct.unpack('>'+'H'*16, self.__font.read(32));
        
    def output(self, x, y, text):
        for char in text:
            fontData = self.getFontData(char);
            if None == fontData:
                continue;
            gdata = [];
            for n in fontData:
                if (n):
                    gdata.append('&H%x'%n);
                else:
                    gdata.append('0');
            self.__out.write('%d DATA %d,%d,%s\r\n'%(self.__line, x, y, ','.join(gdata)));
            self.__nextLine();
            x += 16;

    def __fontDataToAscii(self,fontData):
        result=[];
        for i in range(8):
            oddrow = fontData[i*2];
            evenrow = fontData[i*2+1];
            line = [];
            for j in range(16):
                vodd = oddrow & (1<<(15-j));
                veven = evenrow & (1<<(15-j));
                if vodd:
                    vodd = 1;
                if veven:
                    veven = 1;
                value=(veven<<1)|vodd;
                table=('32','223','230','229');
                line.append(table[value]);
            result.append(line);
        return result;

    def outputAscii(self, x, y, text):
        for char in text:
            fontData = self.getFontData(char);
            if None == fontData:
                continue;
            self.__out.write('%d DATA %d,%d\r\n'%(self.__line, x, y));
            for asciiData in self.__fontDataToAscii(fontData):
                self.__out.write('%d DATA %s\r\n'%(self.__line, ','.join(asciiData)));
                self.__nextLine();
            x+=16;
        
if __name__ == '__main__':
    args = argParser.parse_args();
    out = sys.stdout;
    if None != args.o:
        out = open(args.o, 'w');
    out.write('100 DATA %d\r\n'%(sum([len(item['text']) for item in args.textdisp])));
    textDataMaker = TextDataMaker(args.font, out);
    for item in args.textdisp:
        if 'ascii' == args.mode:
            textDataMaker.outputAscii(item['pos'][0], item['pos'][1], item['text']);
        else:
            textDataMaker.output(item['pos'][0], item['pos'][1], item['text']);
    if out != sys.stdout:
        out.close();
    exit(0);

