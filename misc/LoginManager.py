#!/usr/bin/env python3

import sys, os, time, subprocess, atexit, hashlib, termios;
from select import select;
class Kbhit:
    def __init__(self):
        self.__fd = sys.stdin.fileno();
        self.__new_term = termios.tcgetattr(self.__fd);
        self.__old_term = termios.tcgetattr(self.__fd);
        self.__new_term[3] = (self.__new_term[3] & ~termios.ICANON & ~termios.ECHO);
        self.enable();
        atexit.register(self.disable);

    def enable(self):
        termios.tcsetattr(self.__fd, termios.TCSAFLUSH, self.__new_term);
        
    def disable(self):
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
                timestamp = time.time();
                while (not self.kbhit()):
                    time.sleep(0.1);
                    if (time.time() - timestamp >= timeout):
                        raise TimeoutException(timeout);
            
                ch = self.getch();
                if (None == ch):
                    pass;
                elif (ch in ('\x7F', '\x08')):
                    if (len(_input) > 0):
                        _input = _input[0:-1];
                        self.write(b"\x1b[D \x1b[D");
                elif ("\n" == ch):
                    self.writeln(b'');
                    running = False;
                elif (maxlength == None or len(_input) < maxlength):
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

    def launch(self, cmdline, env_custom, pwd = None):
        self.disable();
        env = os.environ.copy();
        env.update(env_custom);
        if (None != pwd):
            os.chdir(pwd);
        self.__proc = subprocess.Popen(cmdline, env = env);
        self.__proc.wait();
        self.__proc = None;
        self.enable();

class LoginManager(ConsoleManager):
    __proc = None;
    __lang = {
        'username': 'Username: ',
        'password': 'Password: ',
        'login_success': 'Login Success!',
        'login_failed': 'Login Failed!',
        'timeout_msg': 'No user input within %d seconds, exit.',
    };
    def __init__(self, config, welcome=None, encoding = 'UTF-8', timeout = 60, nextLoginDelay = 3, lang = None):
        ConsoleManager.__init__(self, encoding);
        self.__encoding = encoding;
        self.__config = config;
        self.__welcomeMsg = welcome;
        self.__timeout = timeout;
        self.__nextLoginDelay = nextLoginDelay;
        if (None != lang):
            self.__lang = lang;
        atexit.register(self.shutdown);
    
    def shutdown(self):
        if (None != self.__proc):
            self.__proc.kill();

    def __login(self):
        if (None != self.__welcomeMsg):
            self.writeln(self.__welcomeMsg);
            self.writeln(b'');
        self.write(self.__lang['username']);
        username = self.readln(timeout=self.__timeout, maxlength=40);
        self.write(self.__lang['password']);
        password = self.readln(password=True, timeout=self.__timeout, maxlength=40);

        user = self.__config.get(username);
        if (None == user):
            return None;
        sha256handler = hashlib.sha256();
        sha256handler.update(password.encode(self.__encoding));
        hashval = sha256handler.hexdigest();
        if (hashval != user['password']):
            return None;
        return (user['exec'], user['env'], user.get('workdir'));

    def run(self):
        try:
            while True:
                try:
                    loginInfo = self.__login();
                    if None != loginInfo:
                        self.writeln(self.__lang['login_success']);
                        self.launch(loginInfo[0], loginInfo[1]);
                    else: 
                        self.writeln('');
                        self.writeln(self.__lang['login_failed']);
                        time.sleep(self.__nextLoginDelay);
                except KeyboardInterrupt:
                    pass;
                except TimeoutException as e:
                    raise e;
                except Exception as e:
                    print(str(e));
        except TimeoutException as e:
            self.writeln(b'');
            self.writeln((self.__lang['timeout_msg'])%(e.timeout));
            self.writeln(b'');

if __name__ == '__main__':
    import json, argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument('config', metavar='Config', type=str, nargs=1, help='Configuration JSON file');
    args = parser.parse_args();
    config = None;
    try:
        with open(args.config[0]) as f:
            config = json.loads(f.read());
    except Exception as e:
        sys.stderr.write('Failed to load configuration file: ');
        sys.stderr.write(str(e)+'\n');
        exit(1);

    loginManager = LoginManager(
        config = config['config'],
        encoding = config['encoding'],
        welcome = config.get('welcome'),
        lang = config.get('lang'),
    );
    loginManager.run();
    exit(0);

