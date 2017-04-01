#!/usr/bin/env python3

import TX, sysinfo, time, kbhit;

if __name__ == '__main__':
    running = True;
    kbhit.init();
    tx = TX.TX();
    tx.write([
        TX.Clrscr(),
        TX.HideCursor(),
        TX.HideBar(),
        TX.Text('系统信息', {
    	    'x':1, 'y':3, 'size':(24,24),
    	    'font':2, 'fg':1, 'bg':None
        }),
        TX.Color(1),
        TX.Rect(0,30,640,33,True),
        TX.Color(0),
    ]);

    try:
        while running:
            result = sysinfo.SysInfo().fetch();
            tx.write([
                TX.Text('开机时间', {
                    'x':1, 'y':36, 'size':(16,16),
                    'font':0, 'fg':1, 'bg':0
                }),
                TX.Text(result['boot_time'].strftime(' %Y-%m-%dT%H:%M:%S'), {
                    'x':100, 'y':36, 'size':(16,16),
                    'font':0, 'fg':1, 'bg':0
                }),
            ]);
            offset = 18;
            if 'cpu_temp' in result:
                tx.write([
                    TX.Text('CPU温度', {
                        'x':1, 'y':36+offset, 'size':(16,16),
                        'font':0, 'fg':1, 'bg':0
                    }),
                    TX.Text(' %d℃'%(result['cpu_temp'])+'    ', {
                        'x':100, 'y':36+offset, 'size':(16,16),
                        'font':0, 'fg':1, 'bg':0
                    }),
                ]);
                offset += 18;
            if 'gpu_temp' in result:
                tx.write([
                    TX.Text('GPU温度', {
                        'x':1, 'y':36+offset, 'size':(16,16),
                        'font':0, 'fg':1, 'bg':0
                    }),
                    TX.Text(' %d℃'%(result['gpu_temp'])+'    ', {
                        'x':100, 'y':36+offset, 'size':(16,16),
                        'font':0, 'fg':1, 'bg':0
                    }),
                ]);
                offset += 18;
            if 'cpu_usage' in result:
                tx.write([
                    TX.Text('CPU使用率', {
                        'x':1, 'y':36+offset, 'size':(16,16),
                        'font':0, 'fg':1, 'bg':0
                    }),
                    TX.Text(' %.1f%%'%(result['cpu_usage']['overall'] * 100)+'    ', {
                        'x':100, 'y':36+offset, 'size':(16,16),
                        'font':0, 'fg':1, 'bg':0
                    }),
                ]);
                offset += 18;
            if 'mem_usage' in result:
                tx.write([
                    TX.Text('内存使用率', {
                        'x':1, 'y':36+offset, 'size':(16,16),
                        'font':0, 'fg':1, 'bg':0
                    }),
                    TX.Text(' %.1f%%'%(result['mem_usage'] * 100)+'    ', {
                        'x':100, 'y':36+offset, 'size':(16,16),
                        'font':0, 'fg':1, 'bg':0
                    }),
                ]);
                offset += 18;
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

