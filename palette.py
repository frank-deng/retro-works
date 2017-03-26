#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import sys, time, tx;
txInstance = tx.TX();
txInstance.write([
    tx.M(10),
    tx.CL(),
    tx.HideCursor(),
    tx.HideBar(),
]);
width = 40;
height = 30;
for p in range(0,256):
    col = p % (640 / width);
    row = int(p * width / 640);
    txInstance.write([
        tx.CO(p),
        tx.B(col*width, row*height, (col+1)*width-1, (row+1)*height-1),
    ]);
txInstance.write([
    tx.WA(),
    tx.M(3),
    tx.ShowCursor(),
    tx.ShowBar(),
    tx.CL(),
]);

