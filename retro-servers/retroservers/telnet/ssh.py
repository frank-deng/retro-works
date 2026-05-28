import asyncio
import asyncssh
from ..util import Logger,ServerGroup
from ..util.iconv import IConvWrapper
from .util import TelnetServer


class SSHHandler(Logger):
    def __init__(self,reader,writer,config,username,password):
        self._conn=None
        self._session=None
        self._channel=None
        self._tasks=None
        self._loop=asyncio.get_running_loop()
        self._queue=asyncio.Queue()
        self._reader,self._writer=reader,writer
        self._config=config
        self._username=username
        self._password=password
        self._buf_size=config.get('buf_size',4096)

    async def __aenter__(self):
        try:
            self._conn = await asyncssh.connect(
                host=self._config['ssh_host'],
                port=self._config.get('ssh_port',22),
                username=self._username,
                password=self._password,
                known_hosts=None
            )
            self._password=None
            self._channel,self._session=await self._conn.create_session(
                asyncssh.SSHClientSession,
                term_type=self._config.get('term','ansi'),
                term_size=(self._config.get('columns',80),
                           self._config.get('rows',24)),
                encoding=None
            )
            self._session.data_received=self._ssh_read
            self._tasks=(
                asyncio.create_task(self._ssh_to_tcp()),
                asyncio.create_task(self._tcp_to_ssh())
            )
        except Exception:
            await self._cleanup()
            raise

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
            if self._tasks is not None:
                for task in self._tasks:
                    if not task.done():
                        task.cancel()
                await asyncio.gather(*self._tasks)
            if self._conn is not None:
                self._conn.close()
                await self._conn.wait_closed()
        except Exception:
            raise

    def _ssh_read(self,data,_):
        try:
            if not data:
                self._loop.call_soon(self._queue.put_nowait,b"")
                return
            self._queue.put_nowait(data)
        except asyncio.CancelledError:
            self._queue.put_nowait(b"")
        except Exception as e:
            self.logger.error(e,exc_info=True)
            self._queue.put_nowait(b"")

    async def _ssh_to_tcp(self):
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

    async def _tcp_to_ssh(self):
        try:
            while True:
                data=await self._reader.read(self._buf_size)
                if not data:
                    break
                self._channel.write(data)
        except (ConnectionResetError,asyncio.CancelledError,BrokenPipeError):
            pass
        except Exception as e:
            self.logger.error(e,exc_info=True)
        finally:
            self._channel.close()
            await self._channel.wait_closed()


class TelnetServerSSHInstance(TelnetServer):
    def __init__(self,config):
        super().__init__(config)
        self._config=config

    async def handler(self,reader,writer,username,password):
        try:
            readerIconv,writerIconv=IConvWrapper(reader,writer,
                self._config.get('client_encoding','utf-8'),
                self._config.get('server_encoding','utf-8'))
            async with SSHHandler(readerIconv,writerIconv,self._config,
                                  username,password):
                pass
            return True
        except (asyncssh.misc.PermissionDenied,ConnectionRefusedError):
            return False


class TelnetServerSSH(ServerGroup):
    def __init__(self,config):
        super().__init__(config[self.__class__.__name__],
                         TelnetServerSSHInstance)

