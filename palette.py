#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import sys, time, tx;
txInstance = tx.TX();
txInstance.write([
    tx.Mode(10),
    tx.Clrscr(),
    tx.HideCursor(),
    tx.HideBar(),
]);
width = 40;
height = 30;
for p in range(0,256):
    col = p % (640 / width);
    row = int(p * width / 640);
    txInstance.write([
        tx.Color(p),
        tx.Rect(col*width, row*height, (col+1)*width-1, (row+1)*height-1, True),
    ]);
txInstance.write([
    tx.Pause(),
    tx.Mode(3),
    tx.ShowCursor(),
    tx.ShowBar(),
    tx.Clrscr(),
]);

