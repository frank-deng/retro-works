#!/usr/bin/env python3

import sys, time, TX, subprocess;
from getch import getch;

class TXLogin:
    __tx = None;
    __menu = [
        {
            'name':'特显演示',
            'exec':['./txdemo.py'],
            'key': '1',
        },
        {
            'name':'系统信息',
            'exec':['./txsysinfo.py'],
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
            TX.Clrscr(),
            TX.HideCursor(),
            TX.HideBar(),
            TX.Color(0), TX.Rect(0,0,640,400,True),
            TX.Text('欢迎使用特显终端', {
                'x':124,
                'y':34,
                'size':(24,24),
                'font':2,
                'fg':1,
                'bg':None,
            }),
        ]);

    def __drawMenu(self):
        cnt = 0;
        for item in self.__menu:
            self.__tx.write([
                #TX.DrawButton(120, 136+cnt*30, 200, 25),
                TX.Text('%2d.%s'%(cnt+1, item['name']), {
                    'x':126,
                    'y':136+cnt*30+5,
                    'size':(16,16),
                    'font':0,
                    'fg':1,
                    'bg':None,
                }),
            ]);
            cnt+=1;

    def __exec(self, exe):
        try:
            p = subprocess.Popen(exe);
            p.wait();
        except Exception:
            pass;

    def __exit(self):
        self.__tx.write([
            TX.Color(0), TX.Rect(0,0,640,348,True),
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
                    self.__drawHeader();
                    self.__drawMenu();
                    break;
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

