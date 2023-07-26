#!/usr/bin/env python3

from traceback import format_exc;
import hashlib,sys,time,socket,selectors;
import traceback;
import subprocess,pty,fcntl,os,io,codecs;
import json;
from utils import SocketServer,BaseLogin

class ProcessApp:
    __process=None;
    def __init__(self,args,cwd,environ={},user=None,group=None):
        self.__master, self.__slave = pty.openpty();
        fcntl.fcntl(self.__master, fcntl.F_SETFL, fcntl.fcntl(self.__master, fcntl.F_GETFL) | os.O_NONBLOCK);
        fcntl.fcntl(self.__slave, fcntl.F_SETFL, fcntl.fcntl(self.__slave, fcntl.F_GETFL) | os.O_NONBLOCK);
        env={};
        env.update(environ);
        self.__process=subprocess.Popen(
            args,
            bufsize=0,
            start_new_session=True,
            stdin=self.__slave,
            stdout=self.__slave,
            stderr=self.__slave,
            cwd=cwd,
            env=env,
            user=user,
            group=group
        );

    def close(self):
        if self.__process is None:
            return;
        if self.__process.poll() is None:
            self.__process.kill();
        os.close(self.__slave);
        os.close(self.__master);
        self.__process=None;

    def read(self, data):
        if self.__process is None or self.__process.poll() is not None:
            return None;
        try:
            dataEncoded=data;
            os.write(self.__master, dataEncoded);
            return True;
        except Exception as e:
            sys.stderr.write(format_exc(e)+"\n");
            return None;

    def write(self):
        if self.__process is None or self.__process.poll() is not None:
            return None;
        try:
            content=os.read(self.__master, 1024);
            return content;
        except BlockingIOError:
            return b'';
        except Exception as e:
            sys.stderr.write(format_exc(e)+"\n");
            return None;

class BGProcessApp:
    __process=None;
    def __init__(self,args,cwd,environ={},user=None,group=None):
        self.__master, self.__slave = pty.openpty();
        fcntl.fcntl(self.__master, fcntl.F_SETFL, fcntl.fcntl(self.__master, fcntl.F_GETFL) | os.O_NONBLOCK);
        fcntl.fcntl(self.__slave, fcntl.F_SETFL, fcntl.fcntl(self.__slave, fcntl.F_GETFL) | os.O_NONBLOCK);
        env={};
        env.update(environ);
        ptyPath="/proc/%d/fd/%d"%(os.getpid(),self.__slave);
        argsProc=[]
        for i in range(len(args)):
            if ('%I'==args[i]):
                argsProc.append(ptyPath)
            else:
                argsProc.append(args[i])
        self.__process=subprocess.Popen(
            argsProc,
            bufsize=0,
            start_new_session=True,
            stdin=self.__slave,
            stdout=self.__slave,
            stderr=self.__slave,
            cwd=cwd,
            env=env,
            user=user,
            group=group
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
            sys.stderr.write(format_exc(e)+"\n");
            return None;

    def write(self):
        if self.__process is None:
            return None;
        try:
            return os.read(self.__master, 65536);
        except BlockingIOError:
            return b'';
        except Exception as e:
            sys.stderr.write(format_exc(e)+"\n");
            return None;

class LoginHandler(BaseLogin):
    __loginInfo={};
    __app=None;
    def __init__(self,configFile):
        super().__init__();
        with open(configFile, 'r') as f:
            self.__loginInfo=json.load(f);

    def onLogin(self,_username,_password):
        username=_username.decode('UTF-8');
        password=hashlib.sha256(_password).hexdigest();
        loginInfo=self.__loginInfo.get(username);
        if (loginInfo is None) or password!=loginInfo['password']:
            return b'Invalid Login.\r\n';
        try:
            if 'ProcessApp'==loginInfo['module']:
                env={}
                if loginInfo.get('os_environ',False):
                    env=os.environ.copy();
                env.update(loginInfo.get('environ',{}));
                self.__app=ProcessApp(
                    loginInfo['command'],
                    loginInfo.get('cwd',os.environ['HOME']),
                    env,
                    user=loginInfo.get('user',None),
                    group=loginInfo.get('group',None)
                );
                return b'Success.'+b'\r\n';
            elif 'BGProcessApp'==loginInfo['module']:
                self.__app=BGProcessApp(
                    loginInfo['command'],
                    loginInfo.get('cwd',os.environ['HOME']),
                    loginInfo.get('environ',{}),
                    user=loginInfo.get('user',None),
                    group=loginInfo.get('group',None)
                );
                return b'Success.'+b'\r\n';
            else:
                return b'Invalid app.'+b'\r\n';
        except Exception as e:
            sys.stderr.write('Error during creating application: '+str(e)+"\n");
            return b'Invalid Login.\r\n';

    def __closeApp(self):
        if self.__app:
            try:
                self.__app.close();
            except Exception as e:
                sys.stderr.write(format_exc(e)+"\n");
            self.__app=None;
    
    def read(self,content):
        if self.__app:
            try:
                if self.__app.read(content) is not None:
                    return True;
            except Exception as e:
                print('app-read',e,file=sys.stderr);
            self.__closeApp();
        return super().read(content)

    def write(self):
        output=b'';
        if self.__app:
            try:
                content=self.__app.write();
                if content is not None:
                    return content;
            except Exception as e:
                print('app-write',e,file=sys.stderr);
            self.__closeApp();
            output+=b'\r\n'
        output+=super().write()
        return output

    def close(self):
        self.__closeApp();

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
        default='./telnetd.conf'
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

