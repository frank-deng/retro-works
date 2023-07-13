import sys,time,socket,selectors
import traceback;

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

    def close(self):
        for key, instance in self.__instances.items():
            try:
                instance.close();
            except Exception as e:
                pass;
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