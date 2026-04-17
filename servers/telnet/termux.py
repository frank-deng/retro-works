import asyncio
import os
import sys
import pwd
import pty
import fcntl
import termios
import struct
import hashlib
from util import Logger
from util.tcpserver import TCPServer
from util.iconv import IConvWrapper
from telnet import login
from telnet import TelnetWrapper


class ProcessHandler(Logger):
    def __init__(self,reader,writer,*,buf_size=4096):
        self.__proc=None
        self.__master_fd=None
        self.__slave_fd=None
        self.__pty_reader=None
        self.__tasks=None
        self.__buf_size=buf_size
        self.__reader,self.__writer=reader,writer
        self.__buf_size=buf_size
        self.__loop=asyncio.get_running_loop()
        self.__queue=asyncio.Queue()

    async def __aenter__(self):
        try:
            self.__master_fd,self.__slave_fd=pty.openpty()
            await self.create_subprocess_exec(self.__master_fd,self.__slave_fd)
            os.close(self.__slave_fd)
            os.set_blocking(self.__master_fd,False)
            self.__tasks=(
                asyncio.create_task(self.__pty_to_tcp()),
                asyncio.create_task(self.__tcp_to_pty())
            )
        except Exception as e:
            await self.__cleanup()
            raise
        return self

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        try:
            if self.__tasks is not None:
                await asyncio.wait(self.__tasks,return_when=asyncio.FIRST_COMPLETED)
        except asyncio.CancelledError:
            pass
        finally:
            await self.__cleanup()

    def __fd_ready(self):
        try:
            data=os.read(self.__master_fd,self.__buf_size)
            if not data:
                self.__loop.call_soon(self.__queue.put_nowait,b"")
                return
            self.__queue.put_nowait(data)
        except (OSError,asyncio.CancelledError):
            self.__queue.put_nowait(b"")

    async def __pty_to_tcp(self):
        self.__loop.add_reader(self.__master_fd,self.__fd_ready)
        try:
            while True:
                data=await self.__queue.get()
                if not data:
                    break
                self.__writer.write(data)
                await self.__writer.drain()
        except (ConnectionResetError,asyncio.CancelledError):
            pass
        except Exception as e:
            self.logger.error(e,exc_info=True)
        finally:
            self.__loop.remove_reader(self.__master_fd)

    async def __write_fd(self,data):
        n=None
        while data:
            try:
                n=os.write(self.__master_fd,data)
                data=data[n:]
            except BlockingIOError:
                self.logger.debug(f'Partial data written {n}/{len(data)}')
                await asyncio.sleep(0.01)

    async def __tcp_to_pty(self):
        try:
            while True:
                data=await self.__reader.read(self.__buf_size)
                if not data:
                    break
                await self.__write_fd(data)
        except (ConnectionResetError,OSError,asyncio.CancelledError):
            pass
        except Exception as e:
            self.logger.error(e,exc_info=True)

    async def __cleanup(self):
        try:
            if self.__tasks is not None:
                for task in self.__tasks:
                    if not task.done():
                        task.cancel()
                await asyncio.gather(*self.__tasks)
        except Exception as e:
            self.logger.error(e,exc_info=True)
        finally:
            self.__close_fd(self.__master_fd)
            self.__master_fd=None

    def __close_fd(self,fd):
        try:
            if fd is not None:
                os.close(fd)
        except Exception as e:
            self.logger.error(e,exc_info=True)

    async def create_subprocess_exec(self,slave_fd):
        pass


class TermuxHandler(ProcessHandler):
    def __init__(self,reader,writer,config):
        super().__init__(reader,writer,buf_size=config.get('buf_size',4096))
        self.__username=config['username']
        self.__shell=config.get('shell','bash')
        self.__term=config.get('term','ansi')
        self.__rows=config.get('rows',24)
        self.__columns=config.get('columns',80)

    async def create_subprocess_exec(self,master_fd,slave_fd):
        env={
            'USER':self.__username,
            'SHELL':self.__shell,
            'TERM':self.__term,
        }
        fcntl.ioctl(slave_fd,termios.TIOCSWINSZ,struct.pack('HHHH',
                    self.__rows,self.__columns,0,0))
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
        readerTelnet,writerTelnet=await TelnetWrapper(reader,writer)
        login_failed_count=0
        while login_failed_count<3:
            username,password=await login(readerTelnet,writerTelnet)
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
            readerIconv,writerIconv=IConvWrapper(readerTelnet,writerTelnet,
                self._config.get('client_encoding',None),
                self._config.get('server_encoding','utf-8'))
            async with TermuxHandler(readerIconv,writerIconv,self._config):
                pass

