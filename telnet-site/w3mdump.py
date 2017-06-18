#!/usr/bin/env python3

import os, sys, subprocess, time, tempfile, urllib.request;

import termios;
from select import select;
class Kbhit:
    def __init__(self):
        self.__fd = sys.stdin.fileno();
        self.__new_term = termios.tcgetattr(self.__fd);
        self.__old_term = termios.tcgetattr(self.__fd);
        self.__new_term[3] = (self.__new_term[3] & ~termios.ICANON & ~termios.ECHO);
        termios.tcsetattr(self.__fd, termios.TCSAFLUSH, self.__new_term);

    def restore(self):
        termios.tcsetattr(self.__fd, termios.TCSAFLUSH, self.__old_term);

    def kbhit(self):
        dr,dw,de = select([sys.stdin], [], [], 0);
        return len(dr)>0;

    def getch(self):
        try:
            ch = sys.stdin.read(1);
            if ch == '\x00' or ord(ch) >= 0xA1:
                return ch+sys.stdin.read(1);
            else:
                return ch;
        except Exception as e:
            return None;

def readkey(keys = None):
    key = None;
    while True:
        while (not kbhit.kbhit()):
            time.sleep(0.1);
        key = kbhit.getch();
        if (None == keys or (key in keys)):
            break;
    return key;

if __name__ == '__main__':
    kbhit = Kbhit();
    try:
        stdout = sys.stdout.fileno();
        downloadURL = sys.argv[1];
        os.write(stdout, '请打开您的终端上的文本捕获功能，然后按Enter键继续。\r\n'.encode('GB2312'));
        readkey(('\n',));
        p = subprocess.Popen(['w3m', '-dump', downloadURL]);
        p.wait();
        readkey();
    finally:
        kbhit.restore();
    exit(0);

