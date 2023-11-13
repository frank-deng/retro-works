import time,socket,selectors;
from traceback import print_exc;

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
        self.__finished=False;
        return content;

    def reset(self):
        self.__inputContent=b'';
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
                self.__display+=b'\r\n';
            elif val>=0x20 and val<=0x7e and len(self.__inputContent)<self.__maxLength:
                self.__inputContent+=val.to_bytes(1,'little');
                if(self.__echo):
                    self.__display+=val.to_bytes(1,'little');

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

    def __closeConn(self,conn):
        key=str(conn.fileno())
        self.__instances[key].close()
        del self.__instances[key]
        self.__sel.unregister(conn)
        conn.close()

    def __connHandler(self, conn, mask):
        instance = self.__instances[str(conn.fileno())];
        datar = None
        dataw = None
        try:
            if (mask & selectors.EVENT_READ):
                datar = conn.recv(1024);
                if datar:
                    if not instance.read(datar):
                        self.__closeConn(conn)
                        return
            if (mask & selectors.EVENT_WRITE):
                dataw = instance.write();
                if dataw:
                    conn.sendall(dataw);
                elif dataw is None:
                    self.__closeConn(conn)
                    return
            if (not datar) and (not dataw):
                time.sleep(0.001);
        except Exception as e:
            print_exc()
            self.__closeConn(conn)

    def close(self):
        for key, instance in self.__instances.items():
            try:
                instance.close();
            except Exception as e:
                print_exc()
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
                
class BaseLogin:
    __loginInfo={};
    __action='showLogin';
    __username=b'';
    __password=b'';
    def __init__(self):
        self.__readLine=Readline();

    def onLogin(self,username,password):
        pass;

    def read(self,content):
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
        output=b'';
        output+=self.__readLine.getDisplay();
        action=self.__action;
        if 'showLogin'==action:
            self.__action='inputUserName';
            self.__readLine.reset();
            output+=b'\r\nLogin:';
        elif 'showPassword'==action:
            self.__action='inputPassword';
            output+=b'Password:';
            self.__readLine.reset();
            self.__readLine.setEcho(False);
        elif 'processLogin'==action:
            self.__action='showLogin';
            output+=self.onLogin(self.__username,self.__password);
            self.__username=b'';
            self.__password=b'';
        return output;

