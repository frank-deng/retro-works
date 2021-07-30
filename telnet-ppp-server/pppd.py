#!/usr/bin/env python3

import os, subprocess, fcntl, argparse;
from serverLib import SocketServer;

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

class PppdHandler:
    __process=None;
    def __init__(self,pppd_options):
        self.__master, self.__slave = os.openpty();
        fcntl.fcntl(self.__master, fcntl.F_SETFL, fcntl.fcntl(self.__master, fcntl.F_GETFL) | os.O_NONBLOCK);
        ptyPath="/proc/%d/fd/%d"%(os.getpid(),self.__slave);
        self.__process=subprocess.Popen([
            '/usr/sbin/pppd',
            ptyPath,
            'nodetach',
        ]+pppd_options);

    def close(self):
        if self.__process is None:
            return;
        os.close(self.__slave);
        os.close(self.__master);
        self.__process=None;

    def read(self, data):
        try:
            os.write(self.__master, data);
            return True;
        except Exception as e:
            return None;

    def write(self):
        try:
            return os.read(self.__master, 65536);
        except BlockingIOError:
            return b'';
        except Exception as e:
            return None;

if '__main__'==__name__:
    socketServer=SocketServer(args.host,args.port,PppdHandler,(args.pppd_options,));
    try:
        socketServer.run();
    except KeyboardInterrupt:
        pass;
    finally:
        socketServer.close();
    exit(0);

