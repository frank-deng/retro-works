import asyncio
import os
import pty
import fcntl
import termios
import struct
import hashlib
from ..util import Logger
from ..util.iconv import IConvWrapper
from .util import TelnetServer


class ProcessHandler(Logger):
    def __init__(self,reader,writer,*,buf_size=4096):
        self._proc=None
        self._master_fd=None
        self._slave_fd=None
        self._pty_reader=None
        self._tasks=None
        self._buf_size=buf_size
        self._reader,self._writer=reader,writer
        self._buf_size=buf_size
        self._loop=asyncio.get_running_loop()
        self._queue=asyncio.Queue()

    async def __aenter__(self):
        try:
            self._master_fd,self._slave_fd=pty.openpty()
            await self.create_subprocess_exec(self._master_fd,self._slave_fd)
            os.close(self._slave_fd)
            os.set_blocking(self._master_fd,False)
            self._tasks=(
                asyncio.create_task(self._pty_to_tcp()),
                asyncio.create_task(self._tcp_to_pty())
            )
        except Exception as e:
            await self._cleanup()
            raise
        return self

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        try:
            if self._tasks is not None:
                await asyncio.wait(self._tasks,return_when=asyncio.FIRST_COMPLETED)
        except asyncio.CancelledError:
            pass
        finally:
            await self._cleanup()

    def _fd_ready(self):
        try:
            data=os.read(self._master_fd,self._buf_size)
            if not data:
                self._loop.call_soon(self._queue.put_nowait,b"")
                return
            self._queue.put_nowait(data)
        except (OSError,asyncio.CancelledError):
            self._queue.put_nowait(b"")

    async def _pty_to_tcp(self):
        self._loop.add_reader(self._master_fd,self._fd_ready)
        try:
            while True:
                data=await self._queue.get()
                if not data:
                    break
                self._writer.write(data)
                await self._writer.drain()
        except (ConnectionResetError,asyncio.CancelledError):
            pass
        except Exception as e:
            self.logger.error(e,exc_info=True)
        finally:
            self._loop.remove_reader(self._master_fd)

    async def _write_fd(self,data):
        n=None
        while data:
            try:
                n=os.write(self._master_fd,data)
                data=data[n:]
            except BlockingIOError:
                self.logger.debug(f'Partial data written {n}/{len(data)}')
                await asyncio.sleep(0.01)

    async def _tcp_to_pty(self):
        try:
            while True:
                data=await self._reader.read(self._buf_size)
                if not data:
                    break
                await self._write_fd(data)
        except (ConnectionResetError,OSError,asyncio.CancelledError):
            pass
        except Exception as e:
            self.logger.error(e,exc_info=True)

    async def _cleanup(self):
        try:
            if self._tasks is not None:
                for task in self._tasks:
                    if not task.done():
                        task.cancel()
                await asyncio.gather(*self._tasks)
        except Exception as e:
            self.logger.error(e,exc_info=True)
        finally:
            self._close_fd(self._master_fd)
            self._master_fd=None

    def _close_fd(self,fd):
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
        self._username=config['username']
        self._shell=config.get('shell','bash')
        self._term=config.get('term','ansi')
        self._rows=config.get('rows',24)
        self._columns=config.get('columns',80)

    async def create_subprocess_exec(self,master_fd,slave_fd):
        env={
            'USER':self._username,
            'SHELL':self._shell,
            'TERM':self._term,
        }
        fcntl.ioctl(slave_fd,termios.TIOCSWINSZ,struct.pack('HHHH',
                    self._rows,self._columns,0,0))
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
            os.execl(self._shell,self._shell)
            os._exit(1)


class TelnetServerTermux(TelnetServer):
    def __init__(self,config):
        self._config=config[self.__class__.__name__]
        super().__init__(self._config)

    async def handler(self,reader,writer,username,password):
        if username!=self._config['username'] or \
            hashlib.sha256(password.encode()).hexdigest()!=self._config['password']:
            return False
        readerIconv,writerIconv=IConvWrapper(reader,writer,
            self._config.get('client_encoding',None),
            self._config.get('server_encoding','utf-8'))
        async with TermuxHandler(readerIconv,writerIconv,self._config):
            pass
        return True

