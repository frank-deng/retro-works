#!/usr/bin/env python3

import sys;
from xml.etree import ElementTree as XmlTree;
xmlDoc = XmlTree.parse(sys.argv[1]);
xmlRoot = xmlDoc.getroot();

noteList=[];
for noteXml in xmlRoot.findall('.//note'):
    accidental=None;
    accidentalXml=noteXml.find('.//accidental');
    if None!=accidentalXml:
        accidental=accidentalXml.text;
        if 'natural'==accidental:
            accidental=None;
    print(noteXml.find('.//step').text, noteXml.find('.//octave').text, accidental, noteXml.find('.//type').text);
