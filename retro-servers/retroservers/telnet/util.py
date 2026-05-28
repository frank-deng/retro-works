import asyncio
import telnetlib3
from telnetlib3.guard_shells import ConnectionCounter
from ..util import Logger


async def readline(reader,writer,*,timeout=None,size=70,echo=True):
    inp,inp_len=bytearray(size),0

    async def read_char():
        char=None
        while char is None:
            if timeout is None:
                char=await reader.read(1)
            else:
                char=await asyncio.wait_for(reader.read(1),timeout=timeout)
        return char

    async def handle_backspace():
        nonlocal inp_len
        if inp_len<=0:
            return
        inp_len-=1
        if echo:
            writer.write(b'\x08 \x08')
            await writer.drain()

    async def handle_char(char):
        nonlocal inp_len
        val=int.from_bytes(char,'little')
        if val>=0x20 and val<=0x7e and inp_len<size:
            inp[inp_len]=val
            inp_len+=1
            if echo:
                writer.write(char)
                await writer.drain()

    res=None
    while True:
        char=await read_char()
        if char==b'': #Disconnected
            inp_len=None
            break
        elif char in (b'\x0d',b'\x0a'): #Finished
            writer.write(b'\r\n')
            await writer.drain()
            break
        elif b'\x08'==char: #Backspace
            await handle_backspace()
        else:
            await handle_char(char)

    if inp_len is not None:
        res=bytes(inp[:inp_len])
        # Ignore input after Enter as much as possible
        try:
            await asyncio.wait_for(reader.read(1000),timeout=0.1)
        except asyncio.TimeoutError:
            pass
    return res


async def login(reader,writer,*,timeout=None):
    username=b''
    while username==b'':
        writer.write(b'\r\nLogin:')
        await writer.drain()
        username=await readline(reader,writer,timeout=timeout,echo=True)
    if username is None:
        return None,None
    writer.write(b'Password:')
    await writer.drain()
    password=await readline(reader,writer,timeout=timeout,echo=False)
    if password is None:
        return None,None
    return username,password


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
            if self._conn_counter is not None and not self._conn_counter.try_acquire():
                writer.close()
                return
            login_failed=0
            while self._login_retry is None or login_failed<self._login_retry:
                username,password=await login(reader,writer,
                                              timeout=self._login_timeout)
                if username is None or password is None:
                    break
                if not username:
                    continue
                if not await self.handler(reader,writer,
                                          username.decode(),password.decode()):
                    login_failed+=1
                    writer.write(b'Login Failed.\r\n')
                    await asyncio.gather(writer.drain(),asyncio.sleep(1))
                else:
                    login_failed=0
            if self._conn_counter is not None:
                self._conn_counter.release()
        except Exception as e:
            self.logger.error(e,exc_info=True)

    async def handler(self,reader,writer,username,password):
        return False

