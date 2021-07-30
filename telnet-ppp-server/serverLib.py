import sys,time,socket,select;

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
            if fileno in self.__instances:
                self.__instances.pop(fileno).close();
            socket.close();
        except Exception as e:
            self.__error(e);

    def __error(self,e):
        sys.stderr.write(str(e)+"\n");
    
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
        server.listen(5);
        self.__inputs.append(server);
        while self.__running:
            readable, writable, exceptional = select.select(self.__inputs,self.__outputs,self.__inputs);
            for s in readable:
                if s is server:
                    try:
                        conn, addr = s.accept();
                        conn.setblocking(0);
                        self.__inputs.append(conn);
                        self.__instances[str(conn.fileno())] = self.__handler(*self.__handlerArgs);
                    except Exception as e:
                        self.__error(e);
                else:
                    try:
                        result=True;
                        try:
                            result=self.__instances[str(s.fileno())].read(s.recv(1024));
                        except Exception as e:
                            self.__error(e);
                        if result is None:
                            self.__closeConnection(s);
                        elif s not in self.__outputs:
                            self.__outputs.append(s);
                    except Exception as e:
                        self.__error(e);
                        self.__closeConnection(s);

            for s in writable:
                try:
                    content=b'';
                    try:
                        content=self.__instances[str(s.fileno())].write();
                    except Exception as e:
                        self.__error(e);
                    if content is None:
                        self.__closeConnection(s);
                    else:
                        s.sendall(content);
                        if s in self.__outputs:
                            self.__outputs.remove(s);
                except Exception as e:
                    self.__error(e);
                    self.__closeConnection(s);

            for s in exceptional:
                self.__closeConnection(s);
            time.sleep(0.1);
