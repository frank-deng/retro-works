from serverLib import SocketServer;

class LoginHandler:
    __inputTimeout=10;
    __retryTimeout=2;
    __retryTimestamp=None;
    __inputTimestamp=None;
    __running=True;
    __queue=b'';
    __action='showLogin';
    __inputContent=b'';
    __username=b'';
    __password=b'';
    __app=None;
    def __init__(self):
        pass;

    def __readLine(self,content,maxLength=60,echo=True):
        for val in content:
            if 0x08==val and len(self.__inputContent)>0: #Backspace
                if(echo):
                    self.__queue+=b'\x08 \x08';
                self.__inputContent=self.__inputContent[0:-1];
            elif 0x0d==val or 0x0a==val: #Continue
                return True;
            elif val>=0x20 and val<=0x7e and len(self.__inputContent)<maxLength:
                self.__inputContent+=val.to_bytes(1,'little');
                if(echo):
                    self.__queue+=val.to_bytes(1,'little');
        return None;

    def __processLogin(self,username,password):
        self.__username=b'';
        self.__password=b'';
        return b'\r\n  u:'+self.__username+b'\r\n  p:'+self.__password;
    
    def read(self,content):
        if not self.__running:
            return None;
        action=self.__action;
        if 'inputUserName'==action:
            if self.__readLine(content):
                self.__username=self.__inputContent;
                self.__inputContent=b'';
                self.__action='showPassword';
        elif 'inputPassword'==action:
            if self.__readLine(content,False):
                self.__password=self.__inputContent;
                self.__inputContent=b'';
                self.__action='processLogin';
        return True;

    def write(self):
        if not self.__running:
            return None;
        output=self.__queue;
        self.__queue=b'';
        action=self.__action;
        if 'showLogin'==action:
            self.__action='inputUserName';
            output+=b'\r\nLogin:';
        elif 'showPassword'==action:
            self.__action='inputPassword';
            output+=b'\r\nPassword:';
        elif 'processLogin'==action:
            self.__action='showLogin';
            output+=self.__processLogin(self.__username,self.__password);
        return output;

    def close(self):
        self.__running=False;

if '__main__'==__name__:
    import argparse;
    parser = argparse.ArgumentParser();
    parser.add_argument(
        '--host',
        '-H',
        help='Specify binding host for the PPP server.',
        default=''
    );
    parser.add_argument(
        '--port',
        '-P',
        help='Specify port for the PPP server.',
        type=int,
        default=23
    );
    parser.add_argument('pppd_options', nargs=argparse.REMAINDER, help='Options for telnet-server');
    args = parser.parse_args();

    socketServer=SocketServer(args.host,args.port,LoginHandler);
    try:
        socketServer.run();
    except KeyboardInterrupt:
        pass;
    finally:
        socketServer.close();
    exit(0);
