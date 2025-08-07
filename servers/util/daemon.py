import sys
import platform
import os
import atexit
import errno
import fcntl
import signal
import functools

class DaemonIsRunningError(RuntimeError):
    pass

class DaemonNotRunningError(RuntimeError):
    pass

class DaemonAbnormalExitError(RuntimeError):
    pass

class PIDFileManager:
    __pidfile=None
    __fd=None
    def __init__(self,pidfile:str=None):
        self.__pidfile=pidfile

    def __atexit(self):
        if self.__fd is not None:
            self.__fd.close()
        if self.__pidfile is not None:
            os.remove(self.__pidfile)
            self.__pidfile=None
        atexit.unregister(self.__atexit)

    def is_running(self):
        if self.__pidfile is None or not os.path.isfile(self.__pidfile):
            return False
        with open(self.__pidfile,'r') as f:
            try:
                fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
                return False
            except IOError as e:
                if e.errno not in (errno.EAGAIN, errno.EACCES):
                    raise
                return True

    def start(self):
        if self.__pidfile is None:
            return
        if self.is_running():
            raise DaemonIsRunningError
        self.__fp=open(self.__pidfile,'w')
        fcntl.flock(self.__fp,fcntl.LOCK_EX|fcntl.LOCK_NB)
        self.__fp.write(str(os.getpid()))
        self.__fp.flush()
        atexit.register(self.__atexit)

def __do_detach():
    if 'Windows'==platform.system():
        return True
    if os.fork():
        return False
    os.setsid()
    os.umask(0)
    if os.fork():
        return False
    sys.stdout.flush()
    sys.stderr.flush()
    with open(os.devnull, 'r') as devnull:
        os.dup2(devnull.fileno(),sys.stdin.fileno())
    with open(os.devnull, 'a') as out:
        os.dup2(out.fileno(),sys.stdout.fileno())
        os.dup2(out.fileno(),sys.stderr.fileno())
    return True

def daemonize(key_pidfile:str,key_detach:str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(config,*args,**kwargs):
            pidman=PIDFileManager(config.get(key_pidfile,None))
            if pidman.is_running():
                raise DaemonIsRunningError
            detach=config.get(key_detach,False)
            if not detach or __do_detach():
                pidman.start()
                func(config,*args,**kwargs)
        return wrapper
    return decorator

def stop_daemon(pid_file:str):
    pidman=PIDFileManager(pid_file)
    if not pidman.is_running():
        if os.path.isfile(pid_file):
            raise DaemonAbnormalExitError
        raise DaemonNotRunningError
    with open(pid_file,'r') as f:
        f.seek(0)
        pid=int(f.read().strip())
        os.kill(pid,signal.SIGINT)

