#-*-coding:utf8;-*-
#qpy:3
#qpy:console
SRC_FOLDER='/sdcard/devel/tx/';
DEST_FOLDER='/sdcard/dosbox/floppy/';
SRC_SUFFIX='.txt';
DEST_SUFFIX='';

def txconv(src, dest):
    t = None;
    with open(src, 'r') as f:
        t = [l.strip() for l in f.readlines()];
    t = '\x0e'+'\x0e'.join(t);
    with open(dest, 'wb+') as f:
        f.write(t.encode('gbk'));

import sys,os;
for fname in os.listdir(SRC_FOLDER):
    src = SRC_FOLDER+os.sep+fname;
    fbase, ext = os.path.splitext(fname);
    dest = DEST_FOLDER+os.sep+fbase+DEST_SUFFIX;
    if not os.path.isfile(src) or ext != SRC_SUFFIX:
        continue;
    txconv(src, dest);
