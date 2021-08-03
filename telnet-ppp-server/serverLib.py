import sys,time,socket,select
import traceback;

class SocketServer:
    __addr=('0,0,0,0',8080);
    __inputs=[];
    __outputs=[];
    __instances={};
    __running=True;
    def __init__(self,host,port,handler,args=()):
        self.__addr=(host,port);
        self.__handler=handler;
        self.__handlerArgs=args;
    
    def __closeConnection(self,socket):
        try:
            fileno=str(socket.fileno());
            if socket in self.__inputs:
                self.__inputs.remove(socket);
            if socket in self.__outputs:
                self.__outputs.remove(socket);
            socket.close();
            if fileno in self.__instances:
                self.__instances.pop(fileno).close();
        except Exception as e:
            self.__error('__closeConnection',e);

    def __error(self,*args):
        try:
            print(*args,file=sys.stderr);
        except Exception as e:
            pass;
    
    def close(self):
        self.__running=False;
        for key, instance in self.__instances.items():
            try:
                instance.close();
            except Exception as e:
                pass;
    
    def run(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        server.setblocking(0);
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1);
        server.bind(self.__addr);
        server.listen(1000);
        self.__inputs.append(server);
        while self.__running:
            readable, writable, exceptional = select.select(self.__inputs,self.__outputs,self.__inputs);
            for s in readable:
                if s is server:
                    try:
                        conn, addr = s.accept();
                        conn.setblocking(0);
                        self.__inputs.append(conn);
                        instance=self.__handler(*self.__handlerArgs);
                        self.__instances[str(conn.fileno())] = instance;
                        try:
                            conn.sendall(instance.write());
                        except Exception as e:
                            pass;
                    except Exception as e:
                        self.__error('init',e);
                else:
                    try:
                        fileno=s.fileno();
                        if(-1==fileno):
                            self.__closeConnection(s);
                            continue;
                        result=self.__instances[str(fileno)].read(s.recv(1024));
                        if result is None:
                            self.__closeConnection(s);
                        elif s not in self.__outputs:
                            self.__outputs.append(s);
                    except Exception as e:
                        self.__error('readable',e);
                        self.__closeConnection(s);

            for s in writable:
                try:
                    fileno=s.fileno();
                    if(-1==fileno):
                        self.__closeConnection(s);
                        continue;
                    content=self.__instances[str(fileno)].write();
                    if content is None:
                        self.__closeConnection(s);
                    else:
                        s.sendall(content);
                except Exception as e:
                    self.__error('writable',e);
                    self.__closeConnection(s);

            for s in exceptional:
                self.__closeConnection(s);
            time.sleep(0.01);
