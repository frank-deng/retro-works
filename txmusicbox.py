#!/usr/bin/env python3

import sys, os, time, threading, TX, re;
from getch import getch;

class MusicMgr:
    __pwd = [];
    def __init__(self, root):
        self.__root = root;
    def pwd(self):
        return self.__pwd;
    def chdir(self, _dir):
        if _dir == '..':
            if len(self.__pwd) > 0:
                self.__pwd.pop();
                return True;
            else:
                return False;
        if os.path.isdir(self.__root+'/'+'/'.join(self.__pwd)):
            self.__pwd.append(_dir);
            return True;
        else:
            return False;
    def list(self):
        if len(self.__pwd) > 0:
            result = {'dirs':['..'], 'files':[]};
        else:
            result = {'dirs':[], 'files':[]};
        for item in sorted(os.listdir(self.__root+'/'+'/'.join(self.__pwd))):
            if os.path.isdir(self.__root+'/'+'/'.join(self.__pwd)+'/'+item):
                result['dirs'].append(item);
            else:
                result['files'].append(item);
        return result;

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
    __items = [];
    def __init__(self, tx, musicMgr):
        self.__tx = tx;
        self.__drawFrame();
        self.__clock = ShowClockThread(self.__tx);
        self.__clock.start();
        self.__mgr = musicMgr;
        self.showDir();

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

    def getCurrentIdx(self):
        return self.__sel;

    def showDir(self):
        pwdText = re.sub(r'\/+', '/', '/'+'/'.join(self.__mgr.pwd())+'/');
        self.__tx.write([
            TX.Text(pwdText, {
                'x':4, 'y':32, 'size':(16,16),
                'font':0, 'fg':1, 'bg':None,
            }),
            TX.Color(1), TX.Line(4,50,636,50),
        ]);

        dirs_files = self.__mgr.list();
        self.__items = [];
        for d in dirs_files['dirs']:
            self.__items.append(('d',d));
        for f in dirs_files['files']:
            self.__items.append(('f',f));

        idx = 0;
        txcmd = [];
        for i in self.__items[0:15]:
            if i[0] == 'd':
                text = i[1];
            elif i[0] == 'f':
                text = i[1];
            self.__tx.write([
                TX.Text(' '+text, {
                    'x':4, 'y':53+idx*16, 'size':(16,16),
                    'font':0, 'fg':1, 'bg':None,
                })
            ]);
            idx += 1;
        #self.__tx.write(txcmd);

'''
if __name__ == '__main__':
    musicMgr = MusicMgr(sys.argv[1]);
    print(musicMgr.list());
    print(musicMgr.pwd());
    print(musicMgr.chdir('Bandari - Spring'));
    print(musicMgr.pwd());
    print(musicMgr.list());
    exit(0);
'''

if __name__ == '__main__':
    running = True;
    musicMgr = MusicMgr(sys.argv[1]);
    view = TXMusicBoxView(TX.TX(), musicMgr);
    try:
        while running:
            view.showDir();
            ch = getch();
            if '\x1b' == ch:
                running = False;
    except KeyboardInterrupt:
        pass;
    view.close();
    exit(0);

