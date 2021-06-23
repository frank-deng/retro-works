#!/usr/bin/env python3

import math;
from PIL import Image;

DOS_COLORS = [
	(0x00, 0x00, 0x00), # 0
	(0x00, 0x00, 0xa8), # 1
	(0x00, 0xa8, 0x00), # 2
	(0x00, 0xa8, 0xa8), # 3
	(0xa8, 0x00, 0x00), # 4
	(0xa8, 0x00, 0xa8), # 5
	(0xa8, 0xa8, 0x00), # 6
	(0xa8, 0xa8, 0xa8), # 7
	
	(0x54, 0x54, 0x54), # 8
	(0x54, 0x54, 0xff), # 9
	(0x54, 0xff, 0x54), # 10
	(0x54, 0xff, 0xff), # 11
	(0xff, 0x54, 0x54), # 12
	(0xff, 0x54, 0xff), # 13
	(0xff, 0xff, 0x54), # 14
	(0xff, 0xff, 0xff), # 15
];

def color_distance(a, b):
	return math.sqrt( (a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2 )
	
def getDosColor(color):
    nearest = 0;
    nearestDistance = None;
    for i in range(len(DOS_COLORS)):
        distance = color_distance(color, DOS_COLORS[i]);
        if (None==nearestDistance or distance<nearestDistance):
            nearest = i;
            nearestDistance = distance;
    return nearest

def processRow(image,rowNum):
    result=[];
    for x in range(80):
        pixelUpper=getDosColor(image.getpixel((x, rowNum*2)));
        pixelLower=getDosColor(image.getpixel((x, rowNum*2+1)));
        result.append('0x%x'%((pixelUpper<<4) | pixelLower));
    return result;

def processFrame(filename):
    code=[];
    img = Image.open(filename).convert("RGB");
    for row in range(25):
        code.append(', '.join(processRow(img,row)));
    img.close();
    return ('''\t{
%s
\t}'''%("\t\t"+",\n\t\t".join(code)));

def main():
    code=[];
    for frame in range(12):
        code.append(processFrame('frames/%02d.png'%(frame)));
    result='''#ifndef __IMAGE_H__
#define __IMAGE_H__

static unsigned char FRAMES_DATA[12][2000]={
%s
};

#endif
'''%(',\n'.join(code));
    with open('frames.h', 'w') as f:
        f.write(result);

main();
