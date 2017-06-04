#!/usr/bin/env python3

import sys, os, time, subprocess, kbhit;

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
stdout = sys.stdout.fileno();

class LoginManager():
    __username = '';
    __password = '';
    __action = 0;
    __proc = None;
    def shutdown(self):
        if (None != self.__proc):
            self.__proc.kill();

    def welcome(self):
        os.write(stdout, '*** 欢迎光临我的信息港 ***\r\n'.encode('GB2312'));
        os.write(stdout, '\r\n用户名：'.encode('GB2312'));

    def launch(self):
        if (self.__username in users and self.__password == users[self.__username]):
            os.write(stdout, '登录成功！\r\n'.encode('GB2312'));
            env = os.environ.copy();
            env.update(env_custom);
            self.__proc = subprocess.Popen(['w3m', '-no-mouse'], env = env);
            self.__proc.wait();
            self.__proc = None;
        else:
            #os.write(stdout, ('%s %s\r\n'%(self.__username, self.__password)).encode('GB2312'));
            os.write(stdout, '登录失败！\r\n\r\n'.encode('GB2312'));
        self.welcome();
        self.__action = 0;
        self.__username = '';
        self.__password = '';

    def input(self, char):
        if ("\n" == char):
            if self.__action == 0:
                os.write(stdout, '\r\n密　码：'.encode('GB2312'));
                self.__action = 1;
            elif self.__action == 1:
                os.write(stdout, b'\r\n');
                self.launch();
        elif (self.__action == 0):
            if (char in ('\x7F', '\x08')):
                if (len(self.__username) > 0):
                    self.__username = self.__username[0:-1];
                    os.write(stdout, b"\x1b[D \x1b[D");
            else:
                self.__username += char;
                os.write(stdout, char.encode('ascii'));
        elif (self.__action == 1):
            if (char in ('\x7F', '\x08')):
                if (len(self.__password) > 0):
                    self.__password = self.__password[0:-1];
                    os.write(stdout, b"\x1b[D \x1b[D");
            else:
                self.__password += char;
                os.write(stdout, b'*');

if __name__ == '__main__':
    kbhit.init();
    running = True;
    tick = timeout = 300;
    loginManager = LoginManager();
    loginManager.welcome();
    try:
        while running:
            while (not kbhit.kbhit()) and tick > 0:
                try:
                    time.sleep(0.1);
                    tick -= 1;
                except KeyboardInterrupt:
                    pass;

            if (tick <= 0):
                running = False;
            else:
                tick = timeout;
                ch = kbhit.getch();
                loginManager.input(ch);
        os.write(stdout, b"\r\n\r\n");
    finally:
        kbhit.restore();
        loginManager.shutdown();
    exit(0);

