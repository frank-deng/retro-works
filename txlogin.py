#!/usr/bin/env python3

import sys, time, tx, subprocess;

try:
    import msvcrt;
    def getch():
        return msvcrt.getch();
except ImportError:
    import tty, sys, termios;
    def getch():
        fd = sys.stdin.fileno();
        old_settings = termios.tcgetattr(fd);
        try:
            tty.setraw(sys.stdin.fileno());
            ch = sys.stdin.read(1);
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings);
        return ch;

txout = tx.TX();

if __name__ == '__main__':
    try:
        while True:
            p = subprocess.Popen(['./palette.py']);
            p.wait();
            txout.write([
                tx.Mode(3),
                tx.ShowCursor(),
                tx.ShowBar(),
                tx.Clrscr(),
            ]);
            txout.write('按Enter键进入特显模式……\r\n');
            while (13 != ord(getch()):
                txout.write('按Enter键进入特显模式……\r\n');
    except KeyboardInterrupt:
        pass;
    exit(0);

