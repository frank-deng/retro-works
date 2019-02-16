#!/usr/bin/env python3

'''
Convert image to the appropriate format used by bmp2cga.py using ImageMagick:

    convert source.jpg -colorspace gray -resize 640x400 -background '#000000' -gravity center -extent 640x400 png:- | convert - -resize '640x200!' -monochrome dest.bmp
    bmp2cga.py dest.bmp image.pic
'''

import sys, struct;

#Prepare arguments
inFile = None;
outFile = None;
try:
    inFile = sys.argv[1];
    outFile = sys.argv[2];
except Exception as e:
    sys.stderr.write("Usage: %s BMP_FILE OUTPUT_FILE\n"%sys.argv[0]);
    exit(1);

class BMPFile:
    __fp = None;
    def __init__(self, path):
        self.__fp = open(inFile, 'rb');
        self.__fp.seek(0);
        header = struct.unpack('<2sL4xL4xLLHHL4xLLLL', self.__fp.read(54));
        if (b'BM' != header[0]):
            raise Exception('Not a BMP file.');
        self.__offset = header[2];
        self.width = header[3];
        self.height = header[4];
        if (1 != header[5]):
            raise Exception('Invalid BMP file.');
        bpp = header[6];
        if (640 != self.width or 200 != self.height or 1 != bpp):
            raise Exception('BMP file must be in 640x200 monochrome format.');
        if (0 != header[7]):
            raise Exception('Compressed BMP not supported.');
        self.__lineBytes = int(self.width * bpp / 8);
        self.__lineBytesPadded = self.__lineBytes + self.__lineBytes % 4;

    def getLine(self, line):
        self.__fp.seek(self.__offset + self.__lineBytesPadded * (self.height - line - 1));
        return self.__fp.read(self.__lineBytes);

    def close(self):
        if self.__fp:
            self.__fp.close();
        

# Read source image
bmpFile = None;
try:
    bmpFile = BMPFile(inFile);
except FileNotFoundError:
    sys.stderr.write("Unable to open input file %s.\n"%inFile);
    exit(1);
except Exception as e:
    sys.stderr.write(str(e)+"\n");
    exit(1);

try:
    with open(outFile, 'wb') as fp:
        fp.seek(0);
        fp.write(b'\xfd\x00\xb8\x00\x00\x00\x40');
        for y in range(0,bmpFile.height,2):
            fp.write(bmpFile.getLine(y));
        fp.seek(7+8000+192);
        for y in range(1,bmpFile.height,2):
            fp.write(bmpFile.getLine(y));
        fp.seek(7+8000+192+8000+192);
        fp.write(b'\x1A');
except Exception as e:
    sys.stderr.write(str(e)+"\n");
    exit(1);

bmpFile.close();
exit(0);

