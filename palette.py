#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import sys, time, TX;
tx = TX.TX();
tx.write([
    TX.Mode(10),
    TX.Clrscr(),
    TX.HideCursor(),
    TX.HideBar(),
]);
width = 40;
height = 30;
for p in range(0,256):
    col = p % (640 / width);
    row = int(p * width / 640);
    tx.write([
        TX.Color(p),
        TX.Rect(col*width, row*height, (col+1)*width-1, (row+1)*height-1, True),
    ]);
tx.write([
    TX.Pause(),
    TX.Mode(3),
    TX.ShowCursor(),
    TX.ShowBar(),
    TX.Clrscr(),
]);

