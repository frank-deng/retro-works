import asyncio
import os
import sys
import pwd
import pty
import fcntl
import termios
import struct
import hashlib
from util.tcpserver import TCPServer
from telnet import login
from telnet import ProcessHandler


class TermuxHandler(ProcessHandler):
    def __init__(self,reader,writer,username,*,buf_size=4096,shell='/bin/bash',
                 term='ansi'):
        super().__init__(reader,writer,buf_size=buf_size)
        self.__username=username
        self.__shell=shell
        self.__term=term

    async def create_subprocess_exec(self,master_fd,slave_fd):
        env={
            'USER':self.__username,
            'SHELL':self.__shell,
            'TERM':self.__term,
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
            for key,value in env.items():
                os.environ[key]=value
            cwd=os.environ.get('HOME',None)
            if cwd is not None:
                os.chdir(cwd)
            os.execl(self.__shell,self.__shell)
            os._exit(1)


class TelnetServerTermux(TCPServer):
    def __init__(self,config):
        self._config=config[self.__class__.__name__]
        super().__init__(self._config['port'],
                         host=self._config.get('host','127.0.0.1'),
                         max_conn=self._config.get('max_connection'))

    async def handler(self,reader,writer):
        writer.write(b'\xFF\xFD\x22\xFF\xFB\x01\xFF\xFB\x00\xFF\xFD\x00\r\n')
        await writer.drain()
        try:
            while True:
                dt=await asyncio.wait_for(reader.read(1000),timeout=0.1)
                self.logger.debug(dt)
        except asyncio.TimeoutError:
            pass
        login_failed_count=0
        while login_failed_count<3:
            username,password=await login(reader,writer)
            if username is None or password is None:
                break
            if not username:
                continue
            if username.decode('ascii')!=self._config['username'] or \
                hashlib.sha256(password).hexdigest()!=self._config['password']:
                login_failed_count+=1
                writer.write(b'Login Failed.\r\n')
                await asyncio.gather(writer.drain(),asyncio.sleep(1))
                continue
            login_failed_count=0
            async with TermuxHandler(reader,writer,self._config['username'],
                buf_size=self._config.get('buf_size',4096),
                shell=self._config.get('shell','/bin/bash')):
                pass

