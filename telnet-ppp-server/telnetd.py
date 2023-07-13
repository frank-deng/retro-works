#!/usr/bin/env python3

from serverLib import SocketServer;
from traceback import format_exc;
import hashlib,sys;

class Readline:
    __maxLength=60;
    __echo=True;
    __display=b'';
    __inputContent=b'';
    __finished=False;
    def setEcho(self,value):
        self.__echo=bool(value);

    def setMaxLength(self,value):
        self.__maxLength=value;

    def getDisplay(self):
        content=self.__display;
        self.__display=b'';
        return content;

    def get(self):
        if not self.__finished:
            return None;
        content=self.__inputContent;
        self.__inputContent=b'';
        self.__display=b'';
        self.__finished=False;
        return content;

    def reset(self):
        self.__inputContent=b'';
        self.__display=b'';
        self.__finished=False;

    def write(self,content):
        if self.__finished:
            return;
        for val in content:
            if 0x08==val and len(self.__inputContent)>0: #Backspace
                if(self.__echo):
                    self.__display+=b'\x08 \x08';
                self.__inputContent=self.__inputContent[0:-1];
            elif 0x0d==val or 0x0a==val: #Continue
                self.__finished=True;
            elif val>=0x20 and val<=0x7e and len(self.__inputContent)<self.__maxLength:
                self.__inputContent+=val.to_bytes(1,'little');
                if(self.__echo):
                    self.__display+=val.to_bytes(1,'little');

import socket,select;
class ProxyApp:
    __socket=None;
    def __init__(self,host,port):
        self.__socket=socket.socket();
        self.__socket.settimeout(3);
        self.__socket.connect((host,port));
        self.__socket.setblocking(0);
        self.__socket.settimeout(3);

    def read(self,content):
        if not self.__socket:
            return None;
        try:
            self.__socket.send(content);
        except Exception as e:
            return None;
        return True;

    def write(self):
        if not self.__socket:
            return None;
        try:
            ready = select.select([self.__socket], [], [], 0.1);
            if not ready[0]:
                return b'';
            content=self.__socket.recv(1024);
            if len(content)<=0:
                return None;
            return content;
        except Exception as e:
            return None;
        return b'';

    def close(self):
        if self.__socket:
            self.__socket.close();
            self.__socket=None;

import subprocess,pty,fcntl,os,io,codecs;
class ProcessApp:
    __process=None;
    __rawMode=True;
    def __init__(self,args,cwd,environ={}):
        self.__master, self.__slave = pty.openpty();
        fcntl.fcntl(self.__master, fcntl.F_SETFL, fcntl.fcntl(self.__master, fcntl.F_GETFL) | os.O_NONBLOCK);
        fcntl.fcntl(self.__slave, fcntl.F_SETFL, fcntl.fcntl(self.__slave, fcntl.F_GETFL) | os.O_NONBLOCK);
        env=os.environ.copy();
        env.update(environ);
        self.__process=subprocess.Popen(
            args,
            bufsize=0,
            start_new_session=True,
            stdin=self.__slave,
            stdout=self.__slave,
            stderr=self.__slave,
            cwd=cwd,
            env=env
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

import json;
class LoginHandler:
    __loginInfo={};
    __running=True;
    __action='showLogin';
    __username=b'';
    __password=b'';
    __app=None;
    def __init__(self,configFile):
        self.__readLine=Readline();
        with open(configFile, 'r') as f:
            self.__loginInfo=json.load(f);

    def __processLogin(self,username,password):
        username=self.__username.decode('UTF-8');
        password=hashlib.sha256(self.__password).hexdigest();
        self.__username=b'';
        self.__password=b'';
        loginInfo=self.__loginInfo.get(username);
        if (loginInfo is None) or password!=loginInfo['password']:
            return b'Invalid Login.\r\n';
        try:
            if 'ProxyApp'==loginInfo['module']:
                self.__app=ProxyApp(loginInfo['host'],loginInfo['port']);
                return b'Success.'+b'\r\n';
            if 'ProcessApp'==loginInfo['module']:
                self.__app=ProcessApp(
                    loginInfo['command'],
                    loginInfo.get('cwd',os.environ['HOME']),
                    loginInfo.get('environ',{})
                );
                return b'Success.'+b'\r\n';
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
        self.__action='showLogin';
    
    def read(self,content):
        if not self.__running:
            return None;
        if self.__app:
            try:
                if self.__app.read(content) is not None:
                    return True;
            except Exception as e:
                print('app-read',e,file=sys.stderr);
            self.__closeApp();

        if not len(content):
            return True;

        self.__readLine.write(content);
        inputContent=self.__readLine.get();
        if inputContent is None:
            return True;
        if 'inputUserName'==self.__action:
            self.__readLine.reset();
            if not inputContent:
                self.__username=b'';
                self.__action='showLogin';
            else:
                self.__username=inputContent;
                self.__action='showPassword';
        elif 'inputPassword'==self.__action:
            self.__readLine.reset();
            self.__readLine.setEcho(True);
            self.__password=inputContent;
            self.__action='processLogin';
        return True;

    def write(self):
        if not self.__running:
            return None;
        output=b'';
        if self.__app:
            try:
                content=self.__app.write();
                if content is not None:
                    return content;
            except Exception as e:
                print('app-write',e,file=sys.stderr);
            self.__closeApp();
            output+=b'\r\n';
            
        output+=self.__readLine.getDisplay();
        action=self.__action;
        if 'showLogin'==action:
            self.__action='inputUserName';
            self.__readLine.reset();
            output+=b'\r\nLogin:';
        elif 'showPassword'==action:
            self.__action='inputPassword';
            output+=b'\r\nPassword:';
            self.__readLine.reset();
            self.__readLine.setEcho(False);
        elif 'processLogin'==action:
            self.__action='showLogin';
            output+=b'\r\n'+self.__processLogin(self.__username,self.__password);
        return output;

    def close(self):
        if not self.__running:
            return;
        if self.__app:
            self.__closeApp();
        self.__running=False;

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
