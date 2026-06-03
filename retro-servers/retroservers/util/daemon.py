import sys
import os
import atexit
import errno
import signal
import functools
if 'win32'==sys.platform:
    import win32event
    import win32api
    import winerror
else:
    import fcntl


class DaemonIsRunningError(RuntimeError):
    pass

class DaemonNotRunningError(RuntimeError):
    pass

class DaemonAbnormalExitError(RuntimeError):
    pass

class PIDFileManager:
    def __init__(self,pidfile:str=None):
        self._pidfile=os.path.expanduser(pidfile)
        self._fp=None

    def __atexit(self):
        if self._fp is not None:
            self._fp.close()
        if self._pidfile is not None:
            os.remove(self._pidfile)
            self._pidfile=None
        atexit.unregister(self.__atexit)

    def is_running(self):
        if self._pidfile is None or not os.path.isfile(self._pidfile):
            return False
        with open(self._pidfile,'r') as f:
            try:
                fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
                return False
            except IOError as e:
                if e.errno not in (errno.EAGAIN, errno.EACCES):
                    raise
                return True

    def start(self):
        if self._pidfile is None:
            return
        if self.is_running():
            raise DaemonIsRunningError
        self._fp=open(self._pidfile,'w')
        fcntl.flock(self._fp,fcntl.LOCK_EX|fcntl.LOCK_NB)
        self._fp.write(str(os.getpid()))
        self._fp.flush()
        atexit.register(self.__atexit)

    def start_windows(self):
        if self._pidfile is None:
            return
        self._fp=win32event.CreateMutex(None,True,self._pidfile)
        if win32api.GetLastError()==winerror.ERROR_ALREADY_EXISTS:
            raise DaemonIsRunningError

def _do_detach():
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
            detach=config.get(key_detach,False)
            if 'win32'==sys.platform:
                pidman.start_windows()
                func(config,*args,**kwargs)
            elif pidman.is_running():
                raise DaemonIsRunningError
            elif not detach or _do_detach():
                pidman.start()
                func(config,*args,**kwargs)
        return wrapper
    return decorator

def stop_daemon(pid_file:str):
    pid_file=os.path.expanduser(pid_file)
    pidman=PIDFileManager(pid_file)
    if not pidman.is_running():
        if os.path.isfile(pid_file):
            raise DaemonAbnormalExitError
        raise DaemonNotRunningError
    with open(pid_file,'r') as f:
        f.seek(0)
        pid=int(f.read().strip())
        os.kill(pid,signal.SIGINT)

