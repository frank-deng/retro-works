#!/usr/bin/env python3

'''
A simple UCDOS TX server for Linux, written in Python3.
'''

import os, sys, time, subprocess, pty, fcntl, socket, select, getopt;

LOGIN_CMD = ['txlogin.py'];
#LOGIN_CMD = ['./getch_test.py'];
ENVIRON = {}
HOST_PORT = ('', 2333);

try:
    options, args = getopt.getopt(sys.argv[1:], "hP:");
    for name, value in options:
        if name == '-h':
            raise Exception;
        if name == '-P':
            HOST_PORT = ('', int(value));
        if name == '-E':
            envname, envval = value.split('=');
            ENVIRON[envname] = envval;
except:
    sys.stderr.write('Usage: %s [-P port]\n'%sys.argv[0]);
    exit(1);

class Terminal:
    __active = False;
    def __init__(self):
        self.__master, self.__slave = pty.openpty();
        fcntl.fcntl(self.__master, fcntl.F_SETFL, fcntl.fcntl(self.__master, fcntl.F_GETFL) | os.O_NONBLOCK);
        self.__startProc();

    def __startProc(self):
        global ENVIRON;
        env = os.environ.copy();
        env.update(ENVIRON);
        self.__proc = subprocess.Popen(LOGIN_CMD,
            stdin = self.__slave, stdout = self.__slave, stderr = self.__slave,
            env = env, close_fds = True);

    def close(self):
        self.__active = False;
        self.__proc.kill();
        os.close(self.__slave);
        os.close(self.__master);

    def read(self):
        if (None != self.__proc.poll()):
            self.__startProc();
        try:
            return os.read(self.__master, 65536);
        except BlockingIOError:
            return b'';

    def write(self, data):
        if (None != self.__proc.poll()):
            self.__startProc();
        if self.__active:
            os.write(self.__master, data);
        else:
            self.__active = True;

inputs = [];
outputs = [];
terms = {};
try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    server.setblocking(0);
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1);
    server.bind(HOST_PORT);
    server.listen(5);
    inputs.append(server);
except OSError as e:
    print(str(e));
    exit(1);

try:
    while inputs:
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
                    data = s.recv(1024);
                    if data:
                        terms[str(s.fileno())].write(data);
                        if s not in outputs:
                            outputs.append(s);
                except ConnectionResetError:
                    terms.pop(str(s.fileno())).close();
                    inputs.remove(s);
                    if s in outputs:
                        outputs.remove(s);
                    s.close();

        for s in writable:
            try:
                s.sendall(terms[str(s.fileno())].read());
            except BrokenPipeError:
                terms.pop(str(s.fileno())).close();
                inputs.remove(s);
                if s in outputs:
                    outputs.remove(s);
                s.close();

        for s in exceptional:
            terms.pop(str(s.fileno())).close();
            inputs.remove(s);
            if s in outputs:
                outputs.remove(s);
            s.close();

except KeyboardInterrupt:
    pass;
finally:
    for key, term in terms.items():
        term.close();

