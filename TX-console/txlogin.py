#!/usr/bin/env python3

import sys, time, TX, subprocess, threading, kbhit;
from getch import getch;

class ShowClockThread(threading.Thread):
    __running = True;
    __active = False;
    __lastTime = None;
    def __init__(self, tx):
        threading.Thread.__init__(self);
        self.__tx = tx;
    def shutdown(self):
        self.__running = False;
    def off(self):
        self.__active = False;
    def refresh(self):
        self.__active = True;
        nowTime = time.strftime(' %Y/%m/%d %H:%M:%S', time.localtime(time.time()));
        if (nowTime != self.__lastTime):
            self.__tx.write([
                TX.Text(nowTime, {
                    'x':640-160-2, 'y':1, 'size':(16,16),
                    'font':0, 'fg':0, 'bg':None, 'charSpace':0,
                }),
            ]);
        self.__lastTime = nowTime;
    def run(self):
        while (self.__running):
            if (self.__active):
                self.refresh();
            time.sleep(0.5);

class TXLogin:
    __tx = None;
    __menu = [
        {
            'name': '飞控中心',
            'exec': ['txfgfs.py'],
            'key': '1',
        },
        {
            'name': '猜数字控制台',
            'exec': ['txguessnum.py'],
            'key': '2',
        },
        {
            'name':'2048控制台',
            'exec': ['tx2048.py'],
            'key': '3',
        },
    ];

    def __init__(self, out = None):
        if (None == out):
            self.__tx = TX.TX();
        else:
            self.__tx = TX.TX(out);
        self.__clock = ShowClockThread(self.__tx);
        self.__clock.start();

    def __drawHeader(self):
        self.__tx.write([
            TX.Clrscr(),
            TX.HideCursor(),
            TX.HideBar(),
            TX.Color(0), TX.Rect(0,0,640,400,True),
            TX.Color(1), TX.Rect(0,0,640,18,True), TX.Rect(0,382,640,400,True),
            TX.Color(0),
            TX.Text('主菜单', {
                'x':2, 'y':1, 'size':(16,16),
                'font':0, 'fg':0, 'bg':None,
            }),
            TX.Text('按数字键选择功能，Esc键退出特显模式。', {
                'x':2, 'y':383, 'size':(16,16),
                'font':0, 'fg':0, 'bg':None,
            }),
            TX.Color(1), 
        ]);
        self.__clock.refresh();

    def __drawMenu(self):
        cnt = 0;
        for item in self.__menu:
            self.__tx.write([
                TX.Text(' %s.%s'%(item['key'], item['name']), {
                    'x':2, 'y':20+cnt*20+5, 'size':(16,16),
                    'font':0, 'fg':1, 'bg':None,
                }),
            ]);
            cnt+=1;

    def __exec(self, exe):
        self.__clock.off();
        try:
            p = subprocess.Popen(exe);
            p.wait();
        except Exception:
            pass;
        self.__clock.refresh();
        self.__drawHeader();
        self.__drawMenu();

    def __exit(self):
        self.__clock.off();
        self.__tx.write([
            TX.Color(0), TX.Rect(0,0,640,400,True),
            TX.ShowCursor(),
            TX.ShowBar(),
            TX.Clrscr(),
        ]);

    def main(self):
        self.__drawHeader();
        self.__drawMenu();
        ch = '\x00';
        while ch != '\x1B':
            ch = getch();
            for item in self.__menu:
                if ch == item['key']:
                    self.__exec(item['exec']);
                    break;
        self.__exit();

    def shutdown(self):
        self.__clock.shutdown();

tx = TX.TX();
if __name__ == '__main__':
    txLogin = TXLogin();
    kbhit.init();
    running = True;
    tick = timeout = 300;
    try:
        while running:
            tx.write('按Enter键进入特显模式……\r\n');
            while (not kbhit.kbhit()) and tick > 0:
                time.sleep(0.1);
                tick -= 1;

            if (tick <= 0):
                running = False;
            else:
                tick = timeout;
                ch = kbhit.getch();
                if ch == '\n':
                    txLogin.main();
    except KeyboardInterrupt:
        pass;
    finally:
        txLogin.shutdown();
    exit(0);

