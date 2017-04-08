import time, subprocess, sys, os, signal;

class DaemonCtrl:
    def __init__(self, command, pidFile = None):
        self.__command = command;
        if (None == pidFile):
            self.__pidFile = os.path.join('/var/tmp/', self.__command[0].split(os.sep)[-1]+'.pid');
        else:
            self.__pidFile = pidFile;

    def getpid(self):
        # Check if PID file exists
        if not os.path.isfile(self.__pidFile):
            return None;

        # Check if corresponding process exists
        pid = None;
        with open(self.__pidFile, 'r') as f:
            pid = int(f.readline());
            try:
                os.kill(pid, 0);
            except OSError:
                os.remove(self.__pidFile);
                pid = None;

        # Check if process is `guessnum-stat`
        procOK = False;
        if pid:
            try:
                with open(os.path.join('/proc/', str(pid), 'cmdline'), 'r') as cmd:
                    if (cmd.readline().split('\0')[0] == self.__command[0]):
                        procOK = True;
            except FileNotFoundError:
                pass;

        if not procOK:
            if os.path.isfile(self.__pidFile):
                os.remove(self.__pidFile);
            return None;

        return pid;

    def start(self):
        if None != self.getpid():
            return False;
        process = subprocess.Popen(self.__command);
        with open(self.__pidFile, 'w') as f:
            f.write(str(process.pid));
        time.sleep(1);
        if None != self.getpid():
            return True;
        else:
            return False;

    def stop(self):
        pid = self.getpid();
        if None == pid:
            return False;
        os.kill(pid, signal.SIGINT);
        while None != self.getpid():
            time.sleep(0.1);
        return True;

