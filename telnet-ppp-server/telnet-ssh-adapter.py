#!/usr/bin/env python3

from traceback import print_exc;
import paramiko,socket,json;
from utils import SocketServer,BaseLogin

class SSHApp:
    __trans=None
    __channel=None
    def __init__(self,addr,port,username,password,term=None,width=None,height=None):
        trans=paramiko.Transport((addr,port,))
        trans.start_client()
        trans.auth_password(username, password)
        channel=trans.open_session()
        channel.get_pty(term,width,height)
        channel.invoke_shell()
        channel.setblocking(0)
        self.__trans=trans
        self.__channel=channel

    def close(self):
        try:
            self.__trans.close()
            self.__channel.close()
        except Exception as e:
            print_exc()
        self.__trans=None
        self.__channel=None

    def read(self, data):
        if self.__trans is None or self.__channel is None:
            return None;
        try:
            self.__channel.send(data);
            return True;
        except socket.timeout:
            return True;
        except socket.error:
            return None;
        except Exception as e:
            print_exc()
            return None;

    def write(self):
        if self.__trans is None or self.__channel is None:
            return None;
        try:
            return self.__channel.recv(1024);
        except socket.timeout:
            return b'';
        except socket.error:
            return None;
        except Exception as e:
            print_exc()
            return None;

class LoginHandler(BaseLogin):
    __loginInfo={};
    __app=None;
    def __init__(self,configFile):
        super().__init__();
        with open(configFile, 'r') as f:
            self.__loginInfo=json.load(f);

    def onLogin(self,_username,_password):
        username=_username.decode('UTF-8')
        password=_password.decode('UTF-8')
        loginInfo=self.__loginInfo.get(username)
        if (loginInfo is None):
            return b'Invalid Login.\r\n'
        try:
            self.__app=SSHApp(
                loginInfo.get('addr','127.0.0.1'),
                loginInfo.get('port',22),
                loginInfo.get('user',username),
                password,
                term=loginInfo.get('term','ansi'),
                width=loginInfo.get('cols',80),
                height=loginInfo.get('lines',24)
            )
            return b'Success.\r\n';
        except Exception as e:
            print_exc()
            return b'Invalid Login.\r\n';

    def close(self):
        if self.__app:
            self.__app.close();
            self.__app=None;
    
    def read(self,content):
        if self.__app:
            try:
                if self.__app.read(content) is not None:
                    return True;
            except Exception as e:
                print_exc()
            self.close();
        return super().read(content)

    def write(self):
        output=b'';
        if self.__app:
            try:
                content=self.__app.write();
                if content is not None:
                    return content;
            except Exception as e:
                print_exc()
            self.close();
            output+=b'\r\n'
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
        default='./ssh.conf'
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

