import telnetlib3
from telnetlib3.guard_shells import ConnectionCounter
from ..util import Logger
from ..util.tcpserver import TCPServer
from ..terminal.login import login_loop


class TelnetServer(Logger):
    def __init__(self,config):
        self._host=config.get('host','127.0.0.1')
        self._port=config.get('port',23)
        self._login_retry=config.get('login_retry',None)
        self._login_timeout=config.get('login_timeout',None)
        self._term=config.get('term','ansi')
        self._rows=config.get('rows',24)
        self._columns=config.get('columns',80)
        self._conn_counter=None
        max_conn=config.get('max_connection',None)
        if max_conn is not None:
            self._conn_counter=ConnectionCounter(max_conn)

    async def __aenter__(self):
        self._server=await telnetlib3.create_server(
            host=self._host,
            port=self._port,
            term=self._term,
            cols=self._columns,
            rows=self._rows,
            shell=self._handler,
            force_binary=True,
            encoding=None
        )
        self.logger.info(f'Telnet server at port {self._port}')
        return self

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()

    async def _handler(self,reader,writer):
        try:
            await login_loop(reader,writer,
                             on_session=self.on_session,
                             login_retry=self._login_retry,
                             login_timeout=self._login_timeout,
                             conn_counter=self._conn_counter)
        except Exception as e:
            self.logger.error(e,exc_info=True)

    async def on_session(self,reader,writer,username,password):
        return False


class DialinServer(TCPServer):
    def __init__(self,config):
        super().__init__(config.get('port',23),
                         host=config.get('host','127.0.0.1'),
                         max_conn=config.get('max_connection',None))
        self._login_retry=config.get('login_retry',None)
        self._login_timeout=config.get('login_timeout',None)
        self._term=config.get('term','ansi')
        self._rows=config.get('rows',24)
        self._columns=config.get('columns',80)

    async def handler(self,reader,writer):
        try:
            await login_loop(reader,writer,
                             on_session=self.on_session,
                             login_retry=self._login_retry,
                             login_timeout=self._login_timeout)
        except Exception as e:
            self.logger.error(e,exc_info=True)

    async def on_session(self,reader,writer,username,password):
        return False

