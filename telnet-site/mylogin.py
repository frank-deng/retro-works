#!/usr/bin/env python3

import sys, os, time, subprocess, atexit;

users = {
    'user' : 'user'
}
env_custom = {
    'TERM' : 'ansi43m',
    'LANG' : 'zh_CN.GB2312',
    'LC_ALL' : 'zh_CN.GB2312',
    'LANGUAGE' : 'zh_CN:zh',
    'LINES' : '25',
    'COLUMNS' : '80',
    'WWW_HOME' : 'http://127.0.0.1:8080',
}

import termios;
from select import select;
class Kbhit:
    def __init__(self):
        self.__fd = sys.stdin.fileno();
        self.__new_term = termios.tcgetattr(self.__fd);
        self.__old_term = termios.tcgetattr(self.__fd);
        self.__new_term[3] = (self.__new_term[3] & ~termios.ICANON & ~termios.ECHO);
        termios.tcsetattr(self.__fd, termios.TCSAFLUSH, self.__new_term);
        atexit.register(self.restore);
        
    def restore(self):
        termios.tcsetattr(self.__fd, termios.TCSAFLUSH, self.__old_term);

    def kbhit(self):
        dr,dw,de = select([sys.stdin], [], [], 0);
        return len(dr)>0;

    def getch(self):
        try:
            ch = sys.stdin.read(1);
            if ch == '\x00' or ord(ch) >= 0xA1:
                return ch+sys.stdin.read(1);
            else:
                return ch;
        except Exception as e:
            return None;
            
class TimeoutException(Exception):
    def __init__(self, timeout=0):
        self.timeout = timeout;
        self.message = 'No user input within %d seconds'%timeout;
            
class ConsoleManager(Kbhit):
    __out = sys.stdout.fileno();
    def __init__(self, encoding = 'UTF-8'):
        Kbhit.__init__(self);
        self.__encoding = encoding;
    
    def readln(self, password=False, maxlength=None, timeout=None):
        running = True;
        _input = '';
        while running:
            try:
                tick = 0;
                while (not self.kbhit()):
                    time.sleep(0.1);
                    tick += 1;
                    if (tick >= timeout*10):
                        raise TimeoutException(timeout);
            
                ch = self.getch();
                if (None == ch):
                    pass;
                elif (ch in ('\x7F', '\x08')):
                    if (len(_input) > 0):
                        input = _input[0:-1];
                        self.write(b"\x1b[D \x1b[D");
                elif ("\n" == ch):
                    self.writeln(b'');
                    running = False;
                elif (maxlength == None or len(input) < maxlength):
                    _input += ch;
                    if password:
                        self.write(b'*');
                    else:
                        self.write(ch.encode('ascii'));
            except KeyboardInterrupt:
                pass;
        return _input;
        
    def write(self, text):
        if (isinstance(text, str)):
            os.write(self.__out, text.encode(self.__encoding, 'ignore'));
        else:
            os.write(self.__out, text);
    
    def writeln(self, text):
        if (isinstance(text, str)):
            os.write(self.__out, text.encode(self.__encoding, 'ignore')+b'\r\n');
        else:
            os.write(self.__out, text+b'\r\n');

class LoginManager(ConsoleManager):
    __proc = None;
    def __init__(self, encoding = 'UTF-8', timeout = 60, nextLoginDelay = 3):
        ConsoleManager.__init__(self, encoding);
        self.__timeout = timeout;
        self.__nextLoginDelay = nextLoginDelay;
        atexit.register(self.shutdown);
    
    def shutdown(self):
        if (None != self.__proc):
            self.__proc.kill();

    def __login(self):
        self.writeln('*** 欢迎光临我的信息港 ***');
        self.writeln(b'');
        self.write('用户名：');
        username = self.readln(timeout=self.__timeout, maxlength=40);
        self.write('密　码：');
        password = self.readln(password=True, timeout=self.__timeout, maxlength=40);
        if (username in users and password == users[username]):
            self.writeln('登录成功！');
            return True;
        else:
            self.writeln('登录失败！');
            self.writeln(b'');
            time.sleep(self.__nextLoginDelay);
            return False;

    def __launch(self):
        env = os.environ.copy();
        env.update(env_custom);
        self.__proc = subprocess.Popen(['w3m', '-no-mouse'], env = env);
        self.__proc.wait();
        self.__proc = None;
    
    def run(self):
        try:
            while True:
                try:
                    if self.__login():
                        self.__launch();
                except TimeoutException as e:
                    raise e;
                except Exception as e:
                    print(str(e));
                    time.sleep(3);
        except TimeoutException as e:
            self.writeln(b'');
            self.writeln('%d秒内无用户输入，退出。'%(e.timeout));
            self.writeln(b'');

if __name__ == '__main__':
    loginManager = LoginManager(encoding='GB2312');
    loginManager.run();
    exit(0);

