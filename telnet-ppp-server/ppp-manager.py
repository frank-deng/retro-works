#!/usr/bin/env python3

from traceback import print_exc
import json,hashlib,subprocess,pty,fcntl,os,time
from utils import SocketServer,BaseLogin

class PPPApp:
    __process=None;
    def __init__(self,args):
        self.__master, self.__slave = pty.openpty();
        fcntl.fcntl(self.__master, fcntl.F_SETFL, fcntl.fcntl(self.__master, fcntl.F_GETFL) | os.O_NONBLOCK);
        fcntl.fcntl(self.__slave, fcntl.F_SETFL, fcntl.fcntl(self.__slave, fcntl.F_GETFL) | os.O_NONBLOCK);
        ptyPath="/proc/%d/fd/%d"%(os.getpid(),self.__slave);
        self.__process=subprocess.Popen(
            [
               '/usr/sbin/pppd',
               ptyPath,
            ] + args,
            bufsize=0,
            start_new_session=True,
            stdin=self.__slave,
            stdout=self.__slave,
            stderr=self.__slave
        );

    def close(self):
        if self.__process is None:
            return;
        os.close(self.__slave);
        os.close(self.__master);
        self.__process=None;

    def read(self, data):
        if self.__process is None:
            return None;
        try:
            os.write(self.__master, data);
            return True;
        except Exception as e:
            print_exc()
            return None;

    def write(self):
        if self.__process is None:
            return None;
        try:
            return os.read(self.__master, 65536);
        except BlockingIOError:
            return b'';
        except Exception as e:
            print_exc()
            return None;

class LoginHandler(BaseLogin):
    conn={}
    __loginInfo={};
    __app=None;
    def __init__(self,configFile):
        super().__init__();
        self.__running=True
        with open(configFile, 'r') as f:
            self.__loginInfo=json.load(f);

    def onLogin(self,_username,_password):
        username=_username.decode('UTF-8');
        password=hashlib.sha256(_password).hexdigest();
        loginInfo=self.__loginInfo.get(username);
        if (loginInfo is None) or password!=loginInfo['password']:
            return b'Invalid Login.\r\n';
        try:
            self.__username=username;
            if username in LoginHandler.conn:
                LoginHandler.conn[username].close()
                time.sleep(1)
            self.__app=PPPApp(
                loginInfo['options'],
            );
            LoginHandler.conn[username]=self
            return b'Success.'+b'\r\n';
        except Exception as e:
            print_exc()
            return b'Invalid Login.\r\n';

    def close(self):
        self.__running=False
        if not self.__app:
            return
        try:
            self.__app.close();
            if self.__username in LoginHandler.conn:
                del LoginHandler.conn[self.__username]
        except Exception as e:
            print_exc()
        self.__app=None;
    
    def read(self,content):
        if not self.__running:
            return False
        if self.__app:
            try:
                if self.__app.read(content) is not None:
                    return True;
            except Exception as e:
                print_exc()
            self.close();
            return False
        return super().read(content)

    def write(self):
        if not self.__running:
            return None
        output=b'';
        if self.__app:
            try:
                content=self.__app.write();
                if content is not None:
                    return content;
            except Exception as e:
                print_exc()
            self.close();
            return None
        output+=super().write()
        return output

if '__main__'==__name__:
    import argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument(
        '--host',
        '-H',
        help='Specify binding host for the telnetd server.',
        default=''
    );
    parser.add_argument(
        '--port',
        '-P',
        help='Specify port for the telnetd server.',
        type=int,
        default=23
    );
    parser.add_argument(
        '--config',
        '-c',
        help='Specify config file for the telnetd server.',
        default='./ppp.conf'
    );
    args = parser.parse_args();

    #Test json format
    with open(args.config, 'r') as f:
        loginInfo=json.load(f);

    socketServer=SocketServer(args.host,args.port,LoginHandler,(args.config,));
    try:
        socketServer.run();
    except KeyboardInterrupt:
        pass;
    finally:
        socketServer.close();
    exit(0);

