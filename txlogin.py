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

class TXLogin:
    __tx = None;
    __menu = [
        {
            'name':'调色板测试',
            'exec':['./palette.py'],
            'key': '1',
        },
        {
            'name':'字体测试',
            'exec':['./fonts.py'],
            'key': '2',
        },
    ];

    def __init__(self, out = None):
        if (None == out):
            self.__tx = tx.TX();
        else:
            self.__tx = tx.TX(out);

    def __drawHeader(self):
        self.__tx.write([
            tx.Mode(10),
            tx.Clrscr(),
            tx.HideCursor(),
            tx.HideBar(),
            tx.Color(6),
            tx.Rect(0,0,640,480,True),
            tx.Text('欢迎使用特显终端', {
                'x':224,
                'y':10,
                'size':(24,24),
                'font':2,
                'fg':1,
                'bg':None,
            }),
            tx.Color(1),
            tx.Line(224,38,416,38),
            tx.Line(224,39,416,39),
            tx.Line(224,40,416,40),
        ]);

    def __drawMenu(self):
        cnt = 0;
        for item in self.__menu:
            self.__tx.write([
                tx.Text('%2d. %s'%(cnt+1, item['name']), {
                    'x':24,
                    'y':60+cnt*16,
                    'size':(16,16),
                    'font':0,
                    'fg':1,
                    'bg':None,
                }),
            ]);
            cnt+=1;

    def __exec(self, exe):
        p = subprocess.Popen(exe);
        p.wait();

    def __exit(self):
        self.__tx.write([
            tx.Mode(3),
            tx.ShowCursor(),
            tx.ShowBar(),
            tx.Clrscr(),
        ]);

    def main(self):
        self.__drawHeader();
        self.__drawMenu();
        ch = getch();
        while ch != 'q':
            for item in self.__menu:
                if ch == item['key']:
                    self.__exec(item['exec']);
                break;
            self.__drawHeader();
            self.__drawMenu();
            ch = getch();
        self.__exit();

txout = tx.TX();
if __name__ == '__main__':
    try:
        txLogin = TXLogin();
        while True:
            txout.write('按Enter键进入特显模式……\r\n');
            while 13 != ord(getch()):
                txout.write('按Enter键进入特显模式……\r\n');
            txLogin.main();
    except KeyboardInterrupt:
        pass;
    exit(0);

