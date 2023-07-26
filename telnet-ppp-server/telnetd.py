#!/usr/bin/env python3

from traceback import format_exc;
import hashlib,sys,time,socket,selectors;
import traceback;
import subprocess,pty,fcntl,os,io,codecs;
import json;

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

class SocketServer:
    __addr=('0,0,0,0',8080);
    __instances={};
    def __init__(self,host,port,handler,args=()):
        self.__addr=(host,port);
        self.__handler=handler;
        self.__handlerArgs=args;
    
    def __accept(self, sock, mask):
        conn, addr = sock.accept();
        conn.setblocking(0);
        instance = self.__handler(*self.__handlerArgs);
        self.__instances[str(conn.fileno())] = instance;
        conn.sendall(instance.write());
        self.__sel.register(conn, selectors.EVENT_READ|selectors.EVENT_WRITE, self.__connHandler);

    def __connHandler(self, conn, mask):
        instance = self.__instances[str(conn.fileno())];
        datar = None
        dataw = None
        try:
            if (mask & selectors.EVENT_READ):
                datar = conn.recv(1024);
                if datar:
                    instance.read(datar);
            if (mask & selectors.EVENT_WRITE):
                dataw = instance.write();
                if dataw:
                    conn.sendall(dataw);
            if (not datar) and (not dataw):
                time.sleep(0.001);
        except Exception as e:
            print(e);
            instance.close();
            del self.__instances[str(conn.fileno())];
            self.__sel.unregister(conn);

    def close(self):
        for key, instance in self.__instances.items():
            try:
                instance.close();
            except Exception as e:
                print(e);
        self.__sel.close();

    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        server.setblocking(0);
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1);
        server.bind(self.__addr);
        server.listen(1000);
        self.__sel = selectors.DefaultSelector();
        self.__sel.register(server, selectors.EVENT_READ, self.__accept);
        while True:
            for key, mask in self.__sel.select():
                key.data(key.fileobj, mask);

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
