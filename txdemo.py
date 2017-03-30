#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import sys, time, TX, getch;
tx = TX.TX();
tx.write([
    TX.Mode(10),
    TX.Clrscr(),
    TX.HideCursor(),
    TX.HideBar(),
]);

size = 46;
for i in range(32):
    x = (i % 4) * size*3.5;
    y = int(i / 4) * (size+4);
    tx.write([
    	TX.Text('字体%d'%i, {
    	    'x':x, 'y':y, 'size':(size,size),
    	    'font':i, 'fg':15, 'bg':None
        }),
    ]);
getch.getch();

width = 40;
height = 30;
for p in range(0,256):
    col = p % (640 / width);
    row = int(p * width / 640);
    tx.write([
        TX.Color(p),
        TX.Rect(col*width, row*height, (col+1)*width-1, (row+1)*height-1, True),
    ]);
getch.getch();
tx.write([
    TX.Mode(3),
    TX.ShowCursor(),
    TX.ShowBar(),
    TX.Clrscr(),
]);

