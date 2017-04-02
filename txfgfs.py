#!/usr/bin/env python3

FG_DATA_URL='http://localhost:5410/json/fgreport/';
FG_CRASHED_URL='http://localhost:5410/json/sim/crashed';
FG_FREEZE_STATE_URL='http://localhost:5410/json/sim/freeze/master';

import httplib2, json, TX, time, kbhit, threading;

def getFlightData():
    try:
        result = {};
        h = httplib2.Http();

        resp, content = h.request(FG_DATA_URL);
        data = json.loads(content.decode('UTF-8'));
        for item in data['children']:
            result[item['name']] = item['value'];

        resp, content = h.request(FG_FREEZE_STATE_URL);
        data = json.loads(content.decode('UTF-8'));
        if data.get('value'):
            result['paused'] = True;
        else:
            result['paused'] = False;

        resp, content = h.request(FG_CRASHED_URL);
        data = json.loads(content.decode('UTF-8'));
        if data.get('value'):
            result['crashed'] = True;
        else:
            result['crashed'] = False;

        return result;
    except Exception as e:
        return None;

class ShowClockThread(threading.Thread):
    def __init__(self, tx):
        threading.Thread.__init__(self);
        self.__tx = tx;
    def quit(self):
        self.__running = False;
    def refresh(self):
        self.__tx.write([
            TX.Color(0),
            TX.Text(time.strftime(' %Y-%m-%d %H:%M:%S', time.localtime(time.time())), {
                'x':372, 'y':2, 'size':(24,24),
                'font':0, 'fg':0, 'charSpace':0,
            }),
            TX.Color(1),
        ]);
    def run(self):
        self.__running = True;
        while (self.__running):
            self.refresh();
            time.sleep(0.5);

class TXFgfsView:
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
            TX.Color(0), TX.Rect(0,0,640,400,True),
            TX.Color(1), TX.Rect(0,0,640,28,True),
            TX.Color(1), TX.Rect(0,380,640,400,True),
            TX.Text('飞控中心', {
                'x':4, 'y':2, 'size':(24,24),
                'font':0, 'fg':0, 'bg':None,
            }),
            TX.Color(0),
        ]);

    def update(self, data, redraw = False):
        if (redraw):
            self.__drawFrame();
            self.__clock.refresh();

        self.__tx.write([
            TX.Color(1),
            TX.Text('机型', {
                'x':16, 'y':32, 'size':(16,16),
                'font':0, 'fg':1, 'charSpace':0,
            }),
            TX.Text(' '+data['aircraft'], {
                'x':4, 'y':50, 'size':(24,24),
                'font':0, 'fg':1, 'bg':None, 'charSpace':1,
            }),
        ]);

        if data['longitude-deg'] >= 0:
            dataShow = " %.6fE"%(abs(data['longitude-deg']));
        else:
            dataShow = " %.6fW"%(abs(data['longitude-deg']));
        self.__tx.write([
            TX.Color(1),
            TX.Text('经度', {
                'x':17, 'y':80, 'size':(16,16),
                'font':0, 'fg':1, 'bg':None, 'charSpace':0,
            }),
            TX.Text(dataShow, {
                'x':4, 'y':98, 'size':(24,24),
                'font':0, 'fg':1, 'bg':None, 'charSpace':1,
            }),
        ]);

        if data['latitude-deg'] >= 0:
            dataShow = " %.6fN"%(abs(data['latitude-deg']));
        else:
            dataShow = " %.6fS"%(abs(data['latitude-deg']));
        self.__tx.write([
            TX.Color(1),
            TX.Text('纬度', {
                'x':213, 'y':80, 'size':(16,16),
                'font':0, 'fg':1, 'bg':None, 'charSpace':0,
            }),
            TX.Text(dataShow, {
                'x':200, 'y':98, 'size':(24,24),
                'font':0, 'fg':1, 'bg':None, 'charSpace':1,
            }),
        ]);

        self.__tx.write([
            TX.Color(1),
            TX.Text('飞行时间', {
                'x':17, 'y':128, 'size':(16,16),
                'font':0, 'fg':1, 'bg':None, 'charSpace':0,
            }),
            TX.Text(' '+data['flight-time-string'], {
                'x':4, 'y':146, 'size':(24,24),
                'font':0, 'fg':1, 'bg':None, 'charSpace':1,
            }),
        ]);
        self.__tx.write([
            TX.Color(1),
            TX.Text('剩余时间', {
                'x':213, 'y':128, 'size':(16,16),
                'font':0, 'fg':1, 'bg':None, 'charSpace':0,
            }),
            TX.Text(' '+data['ete-string'], {
                'x':200, 'y':146, 'size':(24,24),
                'font':0, 'fg':1, 'bg':None, 'charSpace':1,
            }),
        ]);
        self.__tx.write([
            TX.Color(1),
            TX.Text('总距离', {
                'x':17, 'y':176, 'size':(16,16),
                'font':0, 'fg':1, 'bg':None, 'charSpace':0,
            }),
            TX.Text(' %.1fnm'%data['total-distance'], {
                'x':4, 'y':194, 'size':(24,24),
                'font':0, 'fg':1, 'bg':None, 'charSpace':1,
            }),
            TX.Text('剩余距离', {
                'x':213, 'y':176, 'size':(16,16),
                'font':0, 'fg':1, 'bg':None, 'charSpace':0,
            }),
            TX.Text(' %.1fnm'%data['distance-remaining-nm'], {
                'x':200, 'y':194, 'size':(24,24),
                'font':0, 'fg':1, 'bg':None, 'charSpace':1,
            }),
            TX.Text('已飞行距离', {
                'x':409, 'y':176, 'size':(16,16),
                'font':0, 'fg':1, 'bg':None, 'charSpace':0,
            }),
            TX.Text(' %.1fnm'%(data['total-distance']-data['distance-remaining-nm']), {
                'x':396, 'y':194, 'size':(24,24),
                'font':0, 'fg':1, 'bg':None, 'charSpace':1,
            }),
        ]);
        if data['crashed']:
            self.__tx.write([
                TX.Text('已坠毁　　', {
                    'x':4, 'y':382, 'size':(16,16),
                    'font':0, 'fg':0, 'bg':None, 'charSpace':0,
                }),
            ]);
        elif data['paused']:
            self.__tx.write([
                TX.Text('已暂停　　', {
                    'x':4, 'y':382, 'size':(16,16),
                    'font':0, 'fg':0, 'bg':None, 'charSpace':0,
                }),
            ]);
        else:
            self.__tx.write([
                TX.Text('飞行中……', {
                    'x':4, 'y':382, 'size':(16,16),
                    'font':0, 'fg':0, 'bg':None, 'charSpace':0,
                }),
            ]);

if __name__ == '__main__':
    running = True;
    kbhit.init();
    view = TXFgfsView(TX.TX());
    try:
        while running:
            data = getFlightData();
            view.update(data);
            if kbhit.kbhit():
                ch = kbhit.getch();
                if '\x1b' == ch:
                    running = False;
                elif 'L' == ch:
                    view.update(data, True);
            if (running):
                time.sleep(1);
    except KeyboardInterrupt:
        pass;
    view.close();
    kbhit.restore();
    exit(0);

