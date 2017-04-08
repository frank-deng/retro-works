#!/usr/bin/env python3

import time, threading, subprocess, sys, os, signal;
import DaemonCtrl, TX, kbhit;

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

class TXGuessnumStatView:
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
            TX.Text('猜数字控制台', {
                'x':4, 'y':2, 'size':(24,24),
                'font':0, 'fg':0, 'bg':None, 'charSpace':0,
            }),
            TX.Text(' 次数', {
                'x':72, 'y':32, 'size':(16,16), 'fg':1,
            }),
            TX.Text(' 百分比', {
                'x':640-72, 'y':32,
            }),
            TX.Line(74, 51, 74, 51+12*20+4),
        ]);
        txcmd = [];
        for i in range(10):
            txcmd.append(TX.Text(' %2d次猜对'%(i+1), {
                'x':0, 'y':55+i*20, 
            }));
        txcmd.append(TX.Text(' 10次以上', {
            'x':0, 'y':55+10*20, 
        }));
        txcmd.append(TX.Text(' 　　失败', {
            'x':0, 'y':55+11*20, 
        }));
        self.__tx.write(txcmd);

    def update(self, proc):
        pres = proc.getResult();
        result = [];
        _sum = 0;
        for i in range(11):
            result.append(pres[i+1]);
            _sum += pres[i+1];
        result.append(pres[11] + pres[12]);
        result.append(pres[0]);
        _sum += result[10] + result[11];

        precent = [];
        for n in result:
            if n == 0:
                precent.append(0);
            else:
                precent.append(float(n)/float(_sum));

        max_val = max(result);

        self.__tx.write([
            TX.Color(0),
            TX.Rect(75, 55, 640-72, 55+20*13,True),
            TX.Color(1),
        ]);
        for i in range(12):
            txcmd = [
                TX.Text(' %.2f%%'%(precent[i] * 100), {
                    'x':640-72, 'y':55+i*20, 'size':(16,16), 'fg':1,
                }),
            ];
            if (result[i]>0):
                txcmd.append(TX.Rect(75, 55+i*20, (640-75-72)*result[i]/max_val + 75, 55+16+i*20, True));

            text_times = ' %d'%(result[i]);
            if (result[i]/max_val < 0.5):
                txcmd.append(TX.Text(text_times, {
                    'x':(640-75-72)*result[i]/max_val + 75 + 1, 'y':55+i*20+3, 'size':(12,12), 'fg':1,
                }));
            else:
                txcmd.append(TX.Text(text_times, {
                    'x':(640-75-72)*result[i]/max_val + 75 - 6*len(text_times) - 6, 'y':55+i*20+3, 'size':(12,12), 'fg':0,
                }));
            self.__tx.write(txcmd);

        if None == proc.getpid():
            self.__tx.write([
                TX.Text('已停止', {
                    'x':4, 'y':382, 'size':(16,16), 'fg':0,
                })
            ]);
        else:
            self.__tx.write([
                TX.Text('运行中', {
                    'x':4, 'y':382, 'size':(16,16), 'fg':0,
                })
            ]);

if __name__ == '__main__':
    running = True;
    counter = 0;
    proc = GuessnumStatCtrl();
    view = TXGuessnumStatView(TX.TX());
    kbhit.init();
    try:
        while running:
            if (counter % 3000) == 0:
                view.update(proc);

            if kbhit.kbhit():
                ch = kbhit.getch();
                if ch == '\x1b':
                    running = False;
                elif ch == 'S':
                    proc.start();
                    view.update(proc);
                elif ch == 'X':
                    proc.stop();
                    view.update(proc);
                elif ch == 'r':
                    view.update(proc);

            if running:
                time.sleep(0.1);
                counter += 1;
    except KeyboardInterrupt:
        pass;
    finally:
        if proc.getpid():
            proc.getResult();
        kbhit.restore();
        view.close();
    exit(0);

