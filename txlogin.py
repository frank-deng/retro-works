#!/usr/bin/env python3

import sys, time, TX, subprocess;
from getch import getch;

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
            self.__tx = TX.TX();
        else:
            self.__tx = TX.TX(out);

    def __drawHeader(self):
        self.__tx.write([
            TX.Mode(10),
            TX.Clrscr(),
            TX.HideCursor(),
            TX.HideBar(),
            TX.Color(3),
            TX.Rect(0,0,640,480,True),
        ]);
        self.__tx.write([
            TX.RenderPCX(0,0,'C:\PCX\MENU.PCX'),
        ]);
        self.__tx.write([
            TX.Text('欢迎使用特显终端', {
                'x':124,
                'y':34,
                'size':(32,32),
                'font':2,
                'fg':0,
                'bg':None,
            }),
        ]);

    def __drawMenu(self):
        cnt = 0;
        for item in self.__menu:
            self.__tx.write([
                TX.Text('%2d. %s'%(cnt+1, item['name']), {
                    'x':120,
                    'y':136+cnt*18,
                    'size':(16,16),
                    'font':0,
                    'fg':0,
                    'bg':None,
                }),
            ]);
            cnt+=1;

    def __exec(self, exe):
        p = subprocess.Popen(exe);
        p.wait();

    def __exit(self):
        self.__tx.write([
            TX.Mode(3),
            TX.ShowCursor(),
            TX.ShowBar(),
            TX.Clrscr(),
        ]);

    def main(self):
        self.__drawHeader();
        self.__drawMenu();
        ch = getch();
        while ch != '\x1B':
            for item in self.__menu:
                if ch == item['key']:
                    self.__exec(item['exec']);
                break;
            self.__drawHeader();
            self.__drawMenu();
            ch = getch();
        self.__exit();

tx = TX.TX();
if __name__ == '__main__':
    try:
        txLogin = TXLogin();
        while True:
            tx.write('按Enter键进入特显模式……\r\n');
            while getch() != '\r':
                tx.write('按Enter键进入特显模式……\r\n');
            txLogin.main();
    except KeyboardInterrupt:
        pass;
    exit(0);

