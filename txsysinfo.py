#!/usr/bin/env python3

import TX, sysinfo, time, kbhit, threading;
tx = TX.TX();

class Graph:
    __lastData = None;
    def __init__(self, x, y, w, h):
        self.__x, self.__y, self.__w, self.__h = x, y, w, h;
        self.__samples = 30;
        self.__drawFrame(True);
        self.__data = [];

    def __drawFrame(self, complete = False):
        global tx;
        x, y, w, h = self.__x, self.__y, self.__w, self.__h;
        if (complete):
            tx.write([
                TX.Color(1),
                TX.Rect(x, y, x+w, y+h),
                TX.Line(x, y+h/2, x+w, y+h/2),
            ]);
        else:
            tx.write([
                TX.Color(1),
                TX.Line(x, y+h/2, x+w, y+h/2),
            ]);

    def update(self, data, refreshDisplay=False):
        global tx;
        data_old = self.__data[:];
        if data < 0:
            data = 0;
        elif data > 1:
            data = 1;
        self.__data.append(data);
        if (len(self.__data) < 2):
            return;
        elif (len(self.__data) > self.__samples):
            self.__data = self.__data[1:];

        x, y, w, h = (self.__x + self.__w - 1), self.__y, self.__w, self.__h;
        unit = w / (self.__samples);

        for i in range(len(self.__data)-1, 0, -1):
            if (len(self.__data) == len(data_old)):
                d0, d1 = data_old[i], data_old[i-1];
                tx.write([
                    TX.Color(0),
                    TX.Line(x, y+1+(h-2)*(1-d0), x-unit, y+1+(h-2)*(1-d1)),
                ]);
            elif (i > 1):
                d0, d1 = data_old[i-1], data_old[i-2];
                tx.write([
                    TX.Color(0),
                    TX.Line(x, y+1+(h-2)*(1-d0), x-unit, y+1+(h-2)*(1-d1)),
                ]);

            d0, d1 = self.__data[i], self.__data[i-1];
            tx.write([
                TX.Color(1),
                TX.Line(x, y+1+(h-2)*(1-d0), x-unit, y+1+(h-2)*(1-d1)),
            ]);
            x -= unit;
        self.__drawFrame(refreshDisplay);

class ShowClockThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self);
    def quit(self):
        self.__running = False;
    def refresh(self):
        tx.write([
            TX.Color(0),
            TX.Text(time.strftime(' %Y-%m-%d %H:%M:%S', time.localtime(time.time())), {
                'x':372, 'y':2, 'size':(24,24),
                'font':0, 'fg':0, 'bg':None, 'charSpace':0,
            }),
            TX.Color(1),
        ]);
    def run(self):
        self.__running = True;
        while (self.__running):
            self.refresh();
            time.sleep(0.5);

class TXSysinfoView:
    def __init__(self):
        self.__drawHeader();
        self.__graph = {};
        self.__graph['cpuTemp'] = Graph(4, 47, 312, 158);
        self.__graph['gpuTemp'] = Graph(324, 47, 312, 158);
        self.__graph['cpuUsage'] = Graph(4, 232, 312, 158);
        self.__graph['memUsage'] = Graph(324, 232, 312, 158);
        self.__clock = ShowClockThread();
        self.__clock.start();

    def __drawHeader(self):
        global tx;
        tx.write([
            TX.Clrscr(),
            TX.HideCursor(),
            TX.HideBar(),
            TX.Color(0), TX.Rect(0,0,640,400,True),
            TX.Color(1), TX.Rect(0,0,640,28,True),
            TX.Text('系统信息', {
                'x':4, 'y':2, 'size':(24,24),
                'font':0, 'fg':0, 'bg':None
            }),
            TX.Color(0),
        ]);

    def close(self):
        global tx;
        tx.write([
            TX.ShowCursor(),
            TX.ShowBar(),
            TX.Clrscr(),
        ]);
        self.__clock.quit();

    def update(self, result, redraw = False):
        global tx;
        if (redraw):
            self.__drawHeader();
            self.__clock.refresh();
        if 'boot_time' in result:
            tx.write([
                TX.Text(' 开机时间', {
                    'x':120, 'y':2, 'size':(12,12),
                    'font':0, 'fg':0, 'bg':None, 'charSpace':0,
                }),
                TX.Text(result['boot_time'].strftime(' %Y-%m-%d %H:%M:%S'), {
                    'x':120, 'y':16, 'size':(12,12),
                    'font':0, 'fg':0, 'bg':None, 'charSpace':0,
                }),
            ]);
        if 'cpu_temp' in result:
            tx.write([
                TX.Text('CPU温度 %d℃  '%result['cpu_temp'], {
                    'x':4, 'y':30, 'size':(16,16),
                    'font':0, 'fg':1, 'bg':None
                }),
            ]);
            self.__graph['cpuTemp'].update((result['cpu_temp']-30)/80.0, redraw);
        if 'gpu_temp' in result:
            tx.write([
                TX.Text('GPU温度 %d℃  '%result['gpu_temp'], {
                    'x':324, 'y':30, 'size':(16,16),
                    'font':0, 'fg':1, 'bg':None
                }),
            ]);
            self.__graph['gpuTemp'].update((result['gpu_temp']-30)/80.0, redraw);
        if 'cpu_usage' in result:
            tx.write([
                TX.Text('CPU使用率 %.1f%%  '%(result['cpu_usage']['overall'] * 100), {
                    'x':4, 'y':215, 'size':(16,16),
                    'font':0, 'fg':1, 'bg':None
                }),
            ]);
            self.__graph['cpuUsage'].update(result['cpu_usage']['overall'], redraw);
        if 'mem_usage' in result:
            tx.write([
                TX.Text('内存使用率 %.1f%%  '%(result['mem_usage'] * 100), {
                    'x':324, 'y':215, 'size':(16,16),
                    'font':0, 'fg':1, 'bg':None
                }),
            ]);
            self.__graph['memUsage'].update(result['mem_usage'], redraw);

if __name__ == '__main__':
    running = True;
    kbhit.init();
    view = TXSysinfoView();
    try:
        while running:
            result = sysinfo.SysInfo().fetch();
            view.update(result);

            if kbhit.kbhit():
                ch = kbhit.getch();
                if '\x1b' == ch:
                    running = False;
                elif 'L' == ch:
                    view.update(result, True);

            if (running):
                time.sleep(1);
    except KeyboardInterrupt:
        pass;
    view.close();
    kbhit.restore();
    exit(0);

