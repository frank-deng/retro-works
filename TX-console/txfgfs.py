#!/usr/bin/env python3

FG_DATA_URL='http://localhost:5410/json/fgreport/';

import time, threading;
import httplib2, json, sysinfo;
import kbhit, TX;

def getFlightData():
    try:
        result = {};
        h = httplib2.Http(timeout=0.8);
        resp, content = h.request(FG_DATA_URL);
        data = json.loads(content.decode('UTF-8'));
        for item in data['children']:
            result[item['name']] = item['value'];
        return result;
    except Exception as e:
        return None;

class ShowClockThread(threading.Thread):
    __lastTime = None;
    def __init__(self, tx):
        threading.Thread.__init__(self);
        self.__tx = tx;
    def quit(self):
        self.__running = False;
    def refresh(self):
        nowTime = time.strftime(' %Y/%m/%d %H:%M:%S', time.localtime(time.time()));
        if (nowTime != self.__lastTime):
            self.__tx.write([
                TX.Text(nowTime, {
                    'x':640-160-2, 'y':1, 'size':(16,16), 'fg':0,
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
            TX.Rect(0,0,640,18,True),
            TX.Rect(0,380,640,400,True),
            TX.Rect(4,60,636,60),
            TX.Text('飞控中心', {
                'x':4, 'y':1, 'size':(16,16),
                'font':0, 'fg':0, 'bg':None, 'charSpace':0,
            }),
            TX.Text('CPU温度', {
                'x':8, 'y':22, 'size':(16,16), 'fg':1,
            }),
            TX.Text('GPU温度', {
                'x':140+8, 'y':22,
            }),
            TX.Text('CPU使用率', {
                'x':140*2+8, 'y':22,
            }),
            TX.Text('内存使用率', {
                'x':140*3+8, 'y':22,
            }),
            TX.Text('（没有飞行任务）', {
                'x':4, 'y':382, 'fg':0,
            }),
        ]);

    def update(self, sysdata, fgdata, redraw = False):
        if (redraw):
            self.__drawFrame();
            self.__clock.refresh();

        self.__tx.write([
            TX.Text(' %d℃  '%sysdata['cpu_temp'], {
                'x':0, 'y':40, 'size':(16,16), 'fg':1,
            }),
            TX.Text(' %d℃  '%sysdata['gpu_temp'], {
                'x':140, 'y':40,
            }),
            TX.Text(' %.1f%%  '%(sysdata['cpu_usage']['overall'] * 100), {
                'x':140*2, 'y':40,
            }),
            TX.Text(' %.1f%%  '%(sysdata['mem_usage'] * 100), {
                'x':140*3, 'y':40,
            }),
        ]);

        if None == fgdata:
            if self.__hasFgData:
                self.__tx.write([
                    TX.Color(0), TX.Rect(0,77,640,379,True),
                    TX.Text('（没有飞行任务）', {
                        'x':4, 'y':382, 'size':(16,16), 'fg':0,
                    }),
                ]);
            self.__hasFgData = False;
            return;

        top_offset = 68;
        line_height = 40;
        col_width = 120;
        if not self.__hasFgData:
            self.__tx.write([
                TX.Text('机型', {
                    'x':8, 'y':top_offset, 'size':(16,16), 'fg':1,
                }),
                TX.Text('经度', {
                    'x':8, 'y':top_offset+line_height,
                }),
                TX.Text('纬度', {
                    'x':col_width+8, 'y':top_offset+line_height,
                }),
                TX.Text('飞行时间', {
                    'x':col_width*2+8, 'y':top_offset+line_height,
                }),
                TX.Text('剩余时间', {
                    'x':col_width*3+8, 'y':top_offset+line_height,
                }),
                TX.Text('总距离', {
                    'x':8, 'y':top_offset+line_height*2,
                }),
                TX.Text('剩余距离', {
                    'x':col_width+8, 'y':top_offset+line_height*2,
                }),
                TX.Text('已飞行距离', {
                    'x':col_width*2+8, 'y':top_offset+line_height*2,
                }),
            ]);
            self.__hasFgData = True;

        if fgdata['longitude-deg'] >= 0:
            fgdata['longitude'] = " %.6fE   "%(abs(fgdata['longitude-deg']));
        else:
            fgdata['longitude'] = " %.6fW   "%(abs(fgdata['longitude-deg']));

        if fgdata['latitude-deg'] >= 0:
            fgdata['latitude'] = " %.6fN   "%(abs(fgdata['latitude-deg']));
        else:
            fgdata['latitude'] = " %.6fS   "%(abs(fgdata['latitude-deg']));

        if fgdata['crashed']:
            statusText = '已坠毁　　　　　';
        elif fgdata['paused']:
            statusText = '已暂停　　　　　';
        else:
            statusText = '飞行中　　　　　';

        self.__tx.write([
            TX.Text(' '+fgdata['aircraft'], {
                'x':0, 'y':top_offset+18, 'size':(16,16), 'fg':1,
            }),
            TX.Text(fgdata['longitude'], {
                'x':0, 'y':top_offset+line_height+18,
            }),
            TX.Text(fgdata['latitude'], {
                'x':col_width, 'y':top_offset+line_height+18,
            }),
            TX.Text(' '+fgdata['flight-time-string']+'   ', {
                'x':col_width*2, 'y':top_offset+line_height+18,
            }),
            TX.Text(' '+fgdata['ete-string']+'   ', {
                'x':col_width*3, 'y':top_offset+line_height+18,
            }),
            TX.Text(' %.1fnm'%fgdata['total-distance'], {
                'x':0, 'y':top_offset+line_height*2+18,
            }),
            TX.Text(' %.1fnm    '%fgdata['distance-remaining-nm'], {
                'x':col_width, 'y':top_offset+line_height*2+18,
            }),
            TX.Text(' %.1fnm    '%(fgdata['total-distance']-fgdata['distance-remaining-nm']), {
                'x':col_width*2, 'y':top_offset+line_height*2+18,
            }),
            TX.Text(statusText, {
                'x':4, 'y':382, 'size':(16,16), 'fg':0,
            }),
        ]);

if __name__ == '__main__':
    running = True;
    kbhit.init();
    view = TXFgfsView(TX.TX());
    tick = 0;
    try:
        while running:
            if (tick % 10 == 0):
                view.update(sysinfo.SysInfo().fetch(), getFlightData());

            if kbhit.kbhit():
                ch = kbhit.getch();
                if '\x1b' == ch:
                    running = False;

            if (running):
                time.sleep(0.1);
                tick += 1;
    except KeyboardInterrupt:
        pass;
    finally:
        view.close();
        kbhit.restore();
    exit(0);

