#!/usr/bin/env python3
#-*- coding:utf-8 -*-
import sys, time;
sys.stdout.buffer.write('\x0E[M10CLCU1,0CU2,0KB1,0]'.encode('GBK'));
for p in range(0,256):
    col = p % (640/32);
    row = int(p * 32 / 640);
    s = '\x0E[CO%dB%d,%d,%d,%d]\r\n'%(p, col*32, row*32, (col+1)*32-1, (row+1)*32-1);
    sys.stdout.buffer.write(s.encode('GBK'));
sys.stdout.buffer.write('\x0E[WA]\r\n'.encode('GBK'));
sys.stdout.buffer.write('\x0E[M3CLCU1,1CU2,1KB1,1]'.encode('GBK'));

