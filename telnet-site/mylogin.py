#!/usr/bin/env python3

import sys, os, time, subprocess;

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
        
    def __enter__(self):
        return self;
    
    def __exit__(self, exc_type, exc_value, traceback):
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
	def __init__(self, timeout=0);
	    self.timeout = timeout;
	    self.message = 'No user input within %d seconds'%timeout;
            
class ConsoleManager(Kbhit):
	__out = sys.stdout.fileno();
	def __init__(self):
		Kbhit.__init__(self);
		
	def __enter__(self):
        return self;
    
    def __exit__(self, exc_type, exc_value, traceback):
    	Kbhit.__exit__(self);
    
    def readln(self, password=False, maxlength=None, timeout=None):
        running = True;
        input = '';
        while running:
        	try:
        	    tick = 0;
                while (not self.kbhit()):
                    time.sleep(0.1);
                    tick += 1;
                    if (tick >= timeout*10):
                        raise TimeoutException(timeout);
            
                ch = kbhit.getch();
                if (None == ch):
            	    pass;
                elif (ch in ('\x7F', '\x08')):
                    if (len(input) > 0):
                        input = input[0:-1];
                        self.write(b"\x1b[D \x1b[D");
                elif ("\n" == ch):
                	self.writeln(b'');
                	running = False;
                else:
                    input += ch;
                    if password:
                    	self.write(b'*');
                    else:
                        self.write(char.encode('ascii'));
            except KeyboardInterrupt:
                pass;
        return input;
        
    def write(self, text):
    	os.write(self.__out, text);
    
    def writeln(self, text):
    	os.write(self.__out, text+b'\r\n');

class LoginManager(ConsoleManager):
    __proc = None;
    def __init__(self):
        ConsoleManager.__init__(self);
		
	def __enter__(self):
        return self;
    
    def __exit__(self, exc_type, exc_value, traceback):
    	if (None != self.__proc):
    	    self.__proc.kill();
    	InputManager.__exit__(self);

    def __login(self):
        self.writeln('*** 欢迎光临我的信息港 ***'.encode('GB2312'));
        self.writeln(b'');
        self.write('用户名：'.encode('GB2312'));
        username = self.readln(timeout=60);
        self.write('密　码：'.encode('GB2312'));
        password = self.readln(password=True,timeout=60);
        if (self.__username in users and self.__password == users[self.__username]):
            self.writeln('登录成功！'.encode('GB2312'));
            return True;
        else:
        	self.writeln('登录失败！'.encode('GB2312'));
            self.writeln(b'');
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
        	self.writeln(('%d秒内无用户输入，退出。'%(e.timeout)).encode('GB2312'));
            self.writeln(b'');

if __name__ == '__main__':
    loginManager = LoginManager();
    loginManager.run();
    exit(0);

