#!/usr/bin/env python3

import time, threading, subprocess, sys, os, signal;
from getch import getch;
import DaemonCtrl, TX;

class GuessnumStatCtrl(DaemonCtrl.DaemonCtrl):
    __executable = '/usr/local/bin/guessnum-stat';
    __dataFile = '/home/frank/.guessnum-stat.txt';
    def __init__(self):
        DaemonCtrl.DaemonCtrl.__init__(self, [self.__executable, self.__dataFile]);

    def getResult(self):
        result = (0,0,0,0,0,0,0,0,0,0,0,0,0);
        pid = self.getpid();
        if None != pid:
            os.kill(pid, signal.SIGUSR1);
            time.sleep(1);
        try:
            with open(self.__dataFile, 'r') as f:
                result = tuple([int(n) for n in f.readlines()]);
        except FileNotFoundError:
            pass;
        return result;

class ShowClockThread(threading.Thread):
    __lastTime = None;
    def __init__(self, tx):
        threading.Thread.__init__(self);
        self.__tx = tx;
    def quit(self):
        self.__running = False;
    def refresh(self):
        nowTime = time.strftime(' %Y-%m-%d %H:%M:%S', time.localtime(time.time()));
        if (nowTime != self.__lastTime):
            self.__tx.write([
                TX.Text(nowTime, {
                    'x':372, 'y':2, 'size':(24,24), 'fg':0,
                }),
            ]);
        self.__lastTime = nowTime;
    def run(self):
        self.__running = True;
        while (self.__running):
            self.refresh();
            time.sleep(0.1);

class TXFgfsView:
    __hasFgData = False;
    def __init__(self, tx):
        self.__tx = tx;
        self.__drawFrame();
        self.__clock = ShowClockThread(self.__tx);
        self.__clock.start();

    def close(self):
        self.__tx.write([
            TX.ShowCursor(),
            TX.ShowBar(),
            TX.Clrscr(),
        ]);
        self.__clock.quit();

    def __drawFrame(self):
        self.__tx.write([
            TX.Clrscr(),
            TX.HideCursor(),
            TX.HideBar(),
            TX.Color(0),
            TX.Rect(0,0,640,400,True),
            TX.Color(1),
            TX.Rect(0,0,640,28,True),
            TX.Rect(0,380,640,400,True),
            TX.Line(4,76,636,76),
            TX.Text('猜数字控制台', {
                'x':4, 'y':2, 'size':(24,24),
                'font':0, 'fg':0, 'bg':None, 'charSpace':0,
            }),
        ]);

    def update(self):
        pass;

if __name__ == '__main__':
    running = True;
    proc = GuessnumStatCtrl();
    try:
        while running:
            ch = getch();
            if ch == '\x1b':
                running = False;
            elif ch == 's':
                print(proc.start());
            elif ch == 'x':
                print(proc.stop());
            elif ch == 'g':
                print(proc.getpid());
            elif ch == 'r':
                print(proc.getResult());
    except KeyboardInterrupt:
        pass;
    finally:
        pass;
    exit(0);

