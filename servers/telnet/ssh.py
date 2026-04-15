import asyncio
import asyncssh
from util import Logger
from util.tcpserver import TCPServer
from telnet import login


class SSHHandler(Logger):
    __password=None
    __conn=None
    __session=None
    __channel=None
    __tasks=None
    def __init__(self,reader,writer,config,username,password):
        self.__loop=asyncio.get_running_loop()
        self.__queue=asyncio.Queue()
        self.__reader,self.__writer=reader,writer
        self.__config=config
        self.__username=username.decode()
        self.__password=password.decode()
        self.__buf_size=self.__config.get('buf_size',4096)

    async def __aenter__(self):
        try:
            self.__conn = await asyncssh.connect(
                host=self.__config['ssh_host'],
                port=self.__config.get('ssh_port',23),
                username=self.__username,
                password=self.__password,
                known_hosts=None
            )
            self.__password=None
            self.__channel,self.__session=await self.__conn.create_session(
                asyncssh.SSHClientSession,
                term_type=self.__config.get('term',None),
                term_size=(80,24),
                encoding=None
            )
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
        self.__session.data_received=self.__ssh_read
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
        except (ConnectionResetError,asyncio.CancelledError):
            pass
        except Exception as e:
            self.logger.error(e,exc_info=True)
        finally:
            self.__channel.close()
            await self.__channel.wait_closed()


class TelnetServerSSH(TCPServer):
    def __init__(self,config):
        self._config=config[self.__class__.__name__]
        super().__init__(self._config['port'],
            host=config.get('host','127.0.0.1'),
            max_conn=config.get('max_connection'))
        self.__login_retry=config.get('login_retry',None)
        self.__login_timeout=config.get('login_timeout',None)

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
            try:
                async with SSHHandler(reader,writer,self.__config,
                                      username,password):
                    login_failed_count=0
                    pass
            except asyncssh.misc.PermissionDenied:
                login_failed_count+=1
                self.__writer.write(b'Login Failed.\r\n')
                await asyncio.gather(writer.drain(),asyncio.sleep(1))

