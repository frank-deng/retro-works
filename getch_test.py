#!/usr/bin/env python3
#-*- coding:utf-8 -*-
from getch import getch;
while True:
    ch = getch();
    for c in ch:
        print(ch, ord(c));

