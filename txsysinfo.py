#!/usr/bin/env python3

import TX, sysinfo, time, kbhit;

class Graph:
    __lastData = None;
    def __init__(self, x, y, w, h, meter):
        self.__x = x;
        self.__y = y;
        self.__w = w;
        self.__h = h;
        self.__meter = meter;
        self.__samples = 30;
        tx.write([
            TX.Color(1),
            TX.Rect(x, y, x+w, y+h),
        ]);
        self.__drawGraph();
        self.__data = [];

    def __drawGraph(self):
        x = self.__x;
        y = self.__y;
        w = self.__w;
        h = self.__h;
        cmd = [
            TX.Color(1),
        ];
        for v in self.__meter:
            cmd.append(TX.Line(x+1, y+h*v, x+w-1, y+h*v));
        tx.write(cmd);

    def update(self, data):
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

        x = self.__x + self.__w - 1;
        y = self.__y;
        w = self.__w;
        h = self.__h;
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
        self.__drawGraph();

if __name__ == '__main__':
    running = True;
    kbhit.init();
    tx = TX.TX();
    tx.write([
        TX.Clrscr(),
        TX.HideCursor(),
        TX.HideBar(),
        TX.Color(1),
        TX.Rect(0,0,640,28,True),
        TX.Text('系统信息', {
    	    'x':4, 'y':2, 'size':(24,24),
    	    'font':2, 'fg':0, 'bg':None
        }),
        TX.Color(0),
    ]);

    graphCpuTemp = Graph(4, 47, 312, 158, [0.5]);
    graphGpuTemp = Graph(324, 47, 312, 158, [0.5]);
    graphCpuUsage = Graph(4, 232, 312, 158, [0.5]);
    graphMemUsage = Graph(324, 232, 312, 158, [0.5]);

    try:
        while running:
            result = sysinfo.SysInfo().fetch();
            if 'boot_time' in result:
                tx.write([
                    TX.Color(0),
                    TX.Text(' 开机时间', {
                        'x':320, 'y':2, 'size':(12,12),
                        'font':0, 'fg':0, 'bg':1
                    }),
                    TX.Text(result['boot_time'].strftime(' %Y-%m-%d %H:%M:%S'), {
                        'x':320, 'y':16, 'size':(12,12),
                        'font':0, 'fg':0, 'bg':1
                    }),
                    TX.Color(1),
                ]);
            if 'cpu_temp' in result:
                tx.write([
                    TX.Text('CPU温度 %d℃  '%result['cpu_temp'], {
                        'x':4, 'y':30, 'size':(16,16),
                        'font':0, 'fg':1, 'bg':0
                    }),
                ]);
                graphCpuTemp.update((result['cpu_temp']-30)/80.0);
            if 'gpu_temp' in result:
                tx.write([
                    TX.Text('GPU温度 %d℃  '%result['gpu_temp'], {
                        'x':324, 'y':30, 'size':(16,16),
                        'font':0, 'fg':1, 'bg':0
                    }),
                ]);
                graphGpuTemp.update((result['gpu_temp']-30)/80.0);
            if 'cpu_usage' in result:
                tx.write([
                    TX.Text('CPU使用率 %.1f%%  '%(result['cpu_usage']['overall'] * 100), {
                        'x':4, 'y':215, 'size':(16,16),
                        'font':0, 'fg':1, 'bg':0
                    }),
                ]);
                graphCpuUsage.update(result['cpu_usage']['overall']);
            if 'mem_usage' in result:
                tx.write([
                    TX.Text('内存使用率 %.1f%%  '%(result['mem_usage'] * 100), {
                        'x':324, 'y':215, 'size':(16,16),
                        'font':0, 'fg':1, 'bg':0
                    }),
                ]);
                graphMemUsage.update(result['mem_usage']);

            if (kbhit.kbhit() and '\x1b' == kbhit.getch()):
                running = False;
            else:
                time.sleep(1);
    except KeyboardInterrupt:
        pass;

    tx.write([
        TX.ShowCursor(),
        TX.ShowBar(),
        TX.Clrscr(),
    ]);
    kbhit.restore();
    exit(0);

