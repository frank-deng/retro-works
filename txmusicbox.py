#!/usr/bin/env python3

import sys, os, time, threading, TX;
from getch import getch;

class MusicFileMgr:
    __pwd = [];
    def __init__(self, root):
        self.__root = root;
    def pwd(self):
        return self.__pwd;
    def chdir(self, _dir):
        if __dir == '..';
            if len(self.__pwd) > 0:
                self.__pwd.pop();
                return True;
            else:
                return False;
        if (os.isdir(self.__root+'/'+'/'.join(self.__pwd))):
            self.__pwd.append(_dir);
            return True;
        else:
            return False;
    def listFiles(self):
        pass;

class ShowClockThread(threading.Thread):
    def __init__(self, tx):
        threading.Thread.__init__(self);
        self.__tx = tx;
    def quit(self):
        self.__running = False;
    def refresh(self):
        self.__tx.write([
            TX.Text(time.strftime(' %Y-%m-%d %H:%M:%S', time.localtime(time.time())), {
                'x':504, 'y':388, 'size':(12,12),
                'font':0, 'fg':0, 'charSpace':0,
            }),
        ]);
    def run(self):
        self.__running = True;
        while (self.__running):
            self.refresh();
            time.sleep(0.5);

class TXMusicBoxView:
    def __init__(self, tx, rootdir):
        self.__tx = tx;
        self.__drawFrame();
        self.__clock = ShowClockThread(self.__tx);
        self.__clock.start();

    def __drawFrame(self):
        self.__tx.write([
            TX.Clrscr(),
            TX.HideCursor(),
            TX.HideBar(),
            TX.Color(0), TX.Rect(0,0,640,400,True),
            TX.Color(1), TX.Rect(0,0,640,28,True),
            TX.Color(1), TX.Rect(0,386,640,400,True),
            TX.Text('我的音乐盒', {
                'x':4, 'y':2, 'size':(24,24),
                'font':0, 'fg':0, 'bg':None,
            }),
            TX.Color(0),
        ]);

    def close(self):
        self.__tx.write([
            TX.ShowCursor(),
            TX.ShowBar(),
            TX.Clrscr(),
        ]);
        self.__clock.quit();

if __name__ == '__main__':
    running = True;
    view = TXMusicBoxView(TX.TX(), sys.argv[1]);
    try:
        while running:
            ch = getch();
            if '\x1b' == ch:
                running = False;
    except KeyboardInterrupt:
        pass;
    view.close();
    exit(0);

