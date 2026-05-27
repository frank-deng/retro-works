import asyncio
import os
import pty
import fcntl
import termios
import struct
import hashlib
import telnetlib3
from telnetlib3.server_pty_shell import pty_shell
from ..util import Logger
from ..util.iconv import IConvWrapper
from .util import login


class TermuxHandler(Logger):
    def __init__(self,reader,writer,config):
        self._tasks=None
        self._username=config['username']
        self._shell=config.get('shell','bash')
        self._buf_size=config.get('buf_size',4096)
        self._reader,self._writer=reader,writer

    async def __aenter__(self):
        try:
            self._reader_s,self._writer_s=await pty_shell(
                self._reader.reader,self._writer.writer,program=self._shell,
                args=None,raw_mode=False)
            self._tasks=(
                asyncio.create_task(self._task_cs()),
                asyncio.create_task(self._task_sc())
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

    async def _cleanup(self):
        try:
            if self.__tasks is not None:
                for task in self.__tasks:
                    if not task.done():
                        task.cancel()
                await asyncio.gather(*self.__tasks)
        except Exception as e:
            self.logger.error(e,exc_info=True)

    async def _task_sc(self):
        try:
            while True:
                data=await self._reader_s.read(self._buf_size)
                if not data:
                    break
                self._writer.write(data)
                await self._writer.drain()
        except (ConnectionResetError,asyncio.CancelledError):
            pass
        except Exception as e:
            self.logger.error(e,exc_info=True)

    async def _task_cs(self):
        try:
            while True:
                data=await self._reader.read(self._buf_size)
                if not data:
                    break
                self._writer_s.write(data)
                await self._writer_s.drain()
        except (ConnectionResetError,OSError,asyncio.CancelledError):
            pass
        except Exception as e:
            self.logger.error(e,exc_info=True)


class TelnetServerTermux(Logger):
    def __init__(self,config):
        self._server=None
        self._config=config[self.__class__.__name__]
        self._host=self._config.get('host','127.0.0.1')
        self._port=self._config['port']
        self._term=config.get('term','ansi')
        self._rows=config.get('rows',24)
        self._columns=config.get('columns',80)
        self._conn_counter=None
        max_conn=config.get('max_connection',None)
        if max_conn is not None:
            self._conn_counter=telnetlib3.guard_shells.ConnectionCounter(max_conn)

    async def __aenter__(self):
        self._server=await telnetlib3.create_server(
            host=self._host,
            port=self._port,
            term=self._term,
            cols=self._columns,
            rows=self._rows,
            shell=self.handler,
            force_binary=True,
            encoding=None
        )
        return self

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        if self._server is not None:
            self._server.close()

    async def handler(self,reader,writer):
        reader.force_binary=True
        writer.force_binary=True
        if self._conn_counter is not None and not self._conn_counter.try_acquire():
            writer.close()
            return
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
            readerIconv,writerIconv=IConvWrapper(reader,writer,
                self._config.get('client_encoding',None),
                self._config.get('server_encoding','utf-8'))
            async with TermuxHandler(readerIconv,writerIconv,self._config):
                pass
        if self._conn_counter is not None:
            self._conn_counter.release()

