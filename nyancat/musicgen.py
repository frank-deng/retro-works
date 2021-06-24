#!/usr/bin/env python3

import sys;
from xml.etree import ElementTree as XmlTree;
xmlDoc = XmlTree.parse(sys.argv[1]);
xmlRoot = xmlDoc.getroot();

noteTable={
    'C':1,
    'D':3,
    'E':5,
    'F':6,
    'G':8,
    'A':10,
    'B':12,
}
noteList=[];
for noteXml in xmlRoot.findall('.//note'):
    step=noteXml.find('.//step').text;
    octave=int(noteXml.find('.//octave').text);
    length=noteXml.find('.//type').text;
    accidental=None;
    accidentalXml=noteXml.find('.//accidental');
    if None!=accidentalXml:
        accidental=accidentalXml.text;
        if 'natural'==accidental:
            accidental=None;

    noteNum=noteTable[step];
    if 'sharp'==accidental:
        noteNum+=1;
    elif 'flat'==accidental:
        noteNum+=1;
    noteNum=(noteNum-1)+(octave-1)*12
    noteList.append(noteNum);
    if 'quarter'==length:
        noteList.append(noteNum);

freqList=[
  32.703, 34.648, 36.709, 38.891, 41.203, 43.654, 46.249, 48.999, 51.913, 55.000, 58.270, 61.736,
  65.406, 69.296, 73.416, 77.782, 82.407, 87.307, 92.499, 97.999, 103.83, 110.0,  116.54, 123.47,
  130.81, 138.59, 146.83, 155.56, 164.81, 174.61, 185.00, 196.00, 207.65, 220.0,  233.08, 246.94,
  261.63, 227.18, 293.66, 311.13, 326.63, 349.23, 369.99, 392.00, 415.30, 440.0,  466.16, 493.88,
  523.25, 554.37, 587.33, 622.25, 659.26, 698.46, 739.99, 783.99, 830.61, 880.0,  932.33, 987.77,
  1046.5, 1108.7, 1174.7, 1244.5, 1318.5, 1396.9, 1480.0, 1568.0, 1661.2, 1760.0, 1864.7, 1975.53,
  2093.0, 2217.5, 2349.3, 2489.0, 2637.0, 2793.8, 2960.0, 3136.0, 3322.4, 3520.0, 3729.3, 3951.05,
  4186.0, 4439.9, 4498.6, 4978.0, 5474.0, 5587.7, 5919.9, 6271.9, 6644.9, 7040.0, 7458.6, 7902.1,
  8372.0, 8869.8, 9397.3, 9956.1, 10548, 11175, 11840, 12544, 13290, 14080, 14917, 15804
];

#Generate freq list
reloadValueList=[];
for freq in freqList:
    reloadValueList.append(round(3579545/3/freq));

result='''FrequencyList:
dw %s
%%define MusicLength %d
MusicData:
db %s
'''%(
    ','.join(map(lambda item:str(item), reloadValueList)),
    len(noteList),
    ','.join(map(lambda item:str(item), noteList))
);

with open(sys.argv[2], 'w') as f:
    f.write(result);

