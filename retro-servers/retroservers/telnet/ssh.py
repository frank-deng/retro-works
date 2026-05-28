import asyncio
import asyncssh
from ..util import Logger,ServerGroup
from ..util.iconv import IConvWrapper
from .util import TelnetServer


class SSHHandler(Logger):
    def __init__(self,reader,writer,config,username,password):
        self.__conn=None
        self.__session=None
        self.__channel=None
        self.__tasks=None
        self.__loop=asyncio.get_running_loop()
        self.__queue=asyncio.Queue()
        self.__reader,self.__writer=reader,writer
        self.__config=config
        self.__username=username
        self.__password=password
        self.__buf_size=config.get('buf_size',4096)

    async def __aenter__(self):
        try:
            self.__conn = await asyncssh.connect(
                host=self.__config['ssh_host'],
                port=self.__config.get('ssh_port',22),
                username=self.__username,
                password=self.__password,
                known_hosts=None
            )
            self.__password=None
            self.__channel,self.__session=await self.__conn.create_session(
                asyncssh.SSHClientSession,
                term_type=self.__config.get('term','ansi'),
                term_size=(self.__config.get('columns',80),
                           self.__config.get('rows',24)),
                encoding=None
            )
            self.__session.data_received=self.__ssh_read
            self.__tasks=(
                asyncio.create_task(self.__ssh_to_tcp()),
                asyncio.create_task(self.__tcp_to_ssh())
            )
        except Exception:
            await self.__cleanup()
            raise

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        try:
            if self.__tasks is not None:
                await asyncio.wait(self.__tasks,return_when=asyncio.FIRST_COMPLETED)
        except asyncio.CancelledError:
            pass
        finally:
            await self.__cleanup()

    async def __cleanup(self):
        try:
            if self.__tasks is not None:
                for task in self.__tasks:
                    if not task.done():
                        task.cancel()
                await asyncio.gather(*self.__tasks)
            if self.__conn is not None:
                self.__conn.close()
                await self.__conn.wait_closed()
        except Exception:
            raise

    def __ssh_read(self,data,_):
        try:
            if not data:
                self.__loop.call_soon(self.__queue.put_nowait,b"")
                return
            self.__queue.put_nowait(data)
        except asyncio.CancelledError:
            self.__queue.put_nowait(b"")
        except Exception as e:
            self.logger.error(e,exc_info=True)
            self.__queue.put_nowait(b"")

    async def __ssh_to_tcp(self):
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

    async def __tcp_to_ssh(self):
        try:
            while True:
                data=await self.__reader.read(self.__buf_size)
                if not data:
                    break
                self.__channel.write(data)
        except (ConnectionResetError,asyncio.CancelledError,BrokenPipeError):
            pass
        except Exception as e:
            self.logger.error(e,exc_info=True)
        finally:
            self.__channel.close()
            await self.__channel.wait_closed()


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
        except asyncssh.misc.PermissionDenied:
            return False


class TelnetServerSSH(ServerGroup):
    def __init__(self,config):
        super().__init__(config[self.__class__.__name__],
                         TelnetServerSSHInstance)

