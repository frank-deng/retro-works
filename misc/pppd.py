#!/usr/bin/env python3

import os, sys, time, subprocess, pty, fcntl, socket, select, argparse;

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
parser.add_argument('pppd_options', nargs=argparse.REMAINDER, help='Options for pppd');
args = parser.parse_args();

class Terminal:
    __closed=False;
    def __init__(self):
        global args;
        self.__master, self.__slave = pty.openpty();
        fcntl.fcntl(self.__master, fcntl.F_SETFL, fcntl.fcntl(self.__master, fcntl.F_GETFL) | os.O_NONBLOCK);
        ptyPath="/proc/"+str(os.getpid())+'/fd/'+str(self.__slave);
        subprocess.Popen(['/usr/sbin/pppd', ptyPath]+args.pppd_options);

    def close(self):
        if self.__closed:
            return;
        os.close(self.__slave);
        os.close(self.__master);
        self.__closed=True;

    def read(self):
        try:
            return os.read(self.__master, 65536);
        except BlockingIOError:
            return b'';

    def write(self, data):
        os.write(self.__master, data);

inputs = [];
outputs = [];
terms = {};
try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    server.setblocking(0);
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
    server.bind((args.host, args.port));
    server.listen(5);
    inputs.append(server);
except OSError as e:
    print(str(e));
    exit(1);

def closeConnection(socket):
    global inputs,outputs,terms;
    fileno=str(socket.fileno());
    if socket in inputs:
        inputs.remove(socket);
    if socket in outputs:
        outputs.remove(socket);
    if fileno in terms:
        terms.pop(fileno).close();
    socket.close();

try:
    while True:
        time.sleep(0.1);
        readable, writable, exceptional = select.select(inputs, outputs, inputs);
        for s in readable:
            if s is server:
                conn, addr = s.accept();
                conn.setblocking(0);
                inputs.append(conn);
                terms[str(conn.fileno())] = Terminal();
            else:
                try:
                    terms[str(s.fileno())].write(s.recv(1024));
                    if s not in outputs:
                        outputs.append(s);
                except Exception as e:
                    print(e);
                    closeConnection(s);

        for s in writable:
            try:
                s.sendall(terms[str(s.fileno())].read());
                if s in outputs:
                    outputs.remove(s);
            except Exception as e:
                print(e);
                closeConnection(s);

        for s in exceptional:
            closeConnection(s);

except KeyboardInterrupt:
    pass;
finally:
    for key, term in terms.items():
        term.close();

