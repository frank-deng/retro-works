import asyncio
import os
import sys
import pam
import pamela
import pwd
import pty
import fcntl
import termios
import struct
from util.tcpserver import TCPServer
from telnet import login
from telnet import ProcessHandler


class UserShellHandler(ProcessHandler):
    def __init__(self,reader,writer,username,*,buf_size=4096,term='ansi'):
        super().__init__(reader,writer,buf_size=buf_size)
        self.__username=username
        self.__userinfo=pwd.getpwnam(username)
        self.__term=term

    async def create_subprocess_exec(self,master_fd,slave_fd):
        env={
            'USER':self.__userinfo.pw_name,
            'HOME':self.__userinfo.pw_dir,
            'SHELL':self.__userinfo.pw_shell,
            'TERM':self.__term,
            'PATH':'/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
        }
        fcntl.ioctl(slave_fd,termios.TIOCSWINSZ,struct.pack('HHHH',24,80,0,0))
        pid=os.fork()
        if pid==0:
            os.close(master_fd)
            os.setsid()
            os.close(os.open(os.ttyname(slave_fd),os.O_RDWR))
            os.dup2(slave_fd,0)
            os.dup2(slave_fd,1)
            os.dup2(slave_fd,2)
            os.close(slave_fd)
            pamela.open_session(self.__userinfo.pw_name)
            os.setgid(self.__userinfo.pw_gid)
            os.setuid(self.__userinfo.pw_uid)
            for key,value in env.items():
                os.environ[key]=value
            os.chdir(self.__userinfo.pw_dir)
            os.execl(self.__userinfo.pw_shell,self.__userinfo.pw_shell,'--login')
            os._exit(1)


class TelnetServerPAM(TCPServer):
    def __init__(self,port,*,host,max_conn):
        self._config=config[self.__class__.__name__]
        super().__init__(self._config['port'],
                         host=self._config.get('host','127.0.0.1'),
                         max_conn=self._config.get('max_connection'))

    async def handler(self,reader,writer):
        login_failed_count=0
        while login_failed_count<3:
            username,password=await login(reader,writer)
            if username is None or password is None:
                break
            p=pam.pam()
            if not p.authenticate(username,password):
                login_failed_count+=1
                writer.write(b'Login Failed.\r\n')
                await asyncio.gather(writer.drain(),asyncio.sleep(1))
                continue
            login_failed_count=0
            async with UserShellHandler(reader,writer,username,
                buf_size=self._config.get('buf_size',4096),
                shell=self._config.get('shell','/bin/bash'),
                term=self._config.get('term','ansi')):
                pass

