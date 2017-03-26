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
            txout.write('按Enter键进入特显模式……\r\n');
            char = ord(getch());
            if (13 == char):
                p = subprocess.Popen(['/home/frank/devel/fun-ucdos/palette.py']);
                p.wait();
                txout.write([
                    tx.M(3),
                    tx.ShowCursor(),
                    tx.ShowBar(),
                    tx.CL(),
                ]);
    except KeyboardInterrupt:
        pass;
    exit(0);

