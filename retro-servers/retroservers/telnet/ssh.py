import asyncio
import asyncssh
import telnetlib3
from ..util import Logger,ServerGroup
from ..util.iconv import IConvWrapper
from .util import login


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
        self.__username=username.decode()
        self.__password=password.decode()
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


class TelnetServerSSHInstance(Logger):
    def __init__(self,config):
        self._config=config
        self._host=self._config.get('host','127.0.0.1')
        self._port=self._config['port']
        self._login_retry=config.get('login_retry',None)
        self._login_timeout=config.get('login_timeout',None)
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

    async def handler(self,reader,writer):
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
            try:
                readerIconv,writerIconv=IConvWrapper(reader,writer,
                    self._config.get('client_encoding',None),
                    self._config.get('server_encoding','utf-8'))
                async with SSHHandler(readerIconv,writerIconv,self._config,
                                      username,password):
                    login_failed_count=0
                    pass
            except asyncssh.misc.PermissionDenied:
                login_failed_count+=1
                writer.write(b'Login Failed.\r\n')
                await asyncio.gather(writer.drain(),asyncio.sleep(1))
        if self._conn_counter is not None:
            self._conn_counter.release()


class TelnetServerSSH(ServerGroup):
    def __init__(self,config):
        super().__init__(config[self.__class__.__name__],
                         TelnetServerSSHInstance)

