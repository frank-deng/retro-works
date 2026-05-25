import asyncio
import re
from util import Logger
from util.tcpserver import TCPServer
from mailcenter import MailCenter


class SMTPError(Exception):
    pass


class SMTPInvalidParamError(SMTPError):
    def __init__(self,msg='Invalid Parameter'):
        self.message=f'501 {msg}'


class SMTPInvalidAddrError(SMTPError):
    def __init__(self,msg='Invalid email address'):
        self.message=f'510 {msg}'


class SMTPUnimplementedCommandError(SMTPError):
    def __init__(self,msg='Unimplemented Command'):
        self.message=f'502 {msg}'


class SMTPHandlerBase(Logger):
    def __init__(self,reader,writer,*,timeout=60,greeting_host=''):
        self._handlerDict={
            'HELO':self._handleNoop,
            'EHLO':self._handleNoop,
            'MAIL':self._handleSrc,
            'RCPT':self._handleRcpt,
            'DATA':self._handleData,
            'NOOP':self._handleNoop,
            'QUIT':self._handleQuit,
            'RSET':self._handleReset,
        }
        self._running=True
        self._reader=reader
        self._writer=writer
        self._timeout=timeout
        self._greeting_host=greeting_host
        self._do_reset()

    async def _handleNoop(self,line):
        pass

    async def _handleQuit(self,line):
        self._running=False

    async def _handleReset(self,line):
        await self.on_reset()

    async def _handleSrc(self,line):
        content=line.decode('iso8859-1','ignore').strip()
        match=re.search(r'^MAIL From:\s*<([^<>\s]+)>',content,re.IGNORECASE)
        if match is None:
            raise SMTPInvalidParamError
        if not await self.set_src(match[1]):
            raise SMTPInvalidAddrError

    async def _handleRcpt(self,line):
        content=line.decode('iso8859-1','ignore').strip()
        match=re.search(r'^RCPT To:\s*<([^<>\s]+)>',content,re.IGNORECASE)
        if match is None:
            raise SMTPInvalidParamError
        if not await self.add_rcpt(match[1]):
            raise SMTPInvalidAddrError

    async def _handleData(self,line):
        self._writer.write(b'354 End data with <CR><LF>.<CR><LF>\r\n')
        await self._writer.drain()
        msg=b''
        while msg.find(b'\r\n.\r\n')<0:
            msg+=await asyncio.wait_for(self._reader.read(512), timeout=self._timeout)
        msg=msg[:msg.find(b'\r\n.\r\n')]
        await self.on_data(msg)

    def _getCmd(self,line):
        if line==b'':
            return None
        cmd=line.decode('iso8859-1','ignore').strip()
        match=re.search(r'^([^\s]+)',cmd)
        if match is None:
            return ''
        return match[1].upper()
    
    async def run(self):
        self._writer.write(f'220 Email Server {self._greeting_host}\r\n'.encode('iso8859-1'))
        while self._running:
            line=b''
            try:
                line=await asyncio.wait_for(self._reader.readuntil(b'\n'),
                                            timeout=self._timeout)
            except asyncio.exceptions.IncompleteReadError:
                self.logger.error(f'Unexpected EOF')
                break
            cmd=self._getCmd(line)
            if cmd is None:
                break
                continue
            try:
                handler=self._handlerDict.get(cmd,None)
                if handler is None:
                    self.logger.debug(f'SMTP unhandled command:{line}')
                    raise SMTPUnimplementedCommandError
                else:
                    await handler(line)
                    self._writer.write(b'250 OK\r\n')
            except SMTPError as e:
                self._writer.write(f'{e.message}\r\n'.encode('iso8859-1',errors='ignore'))
            except Exception as e:
                self.logger.error(e,exc_info=True)
                self._writer.write(b'451 4.3.0 Internal server rror\r\n')
            finally:
                await self._writer.drain()


class SMTPHandler(SMTPHandlerBase):
    def __init__(self,mailCenter,reader,writer,*,timeout=60,
                 greeting_host=''):
        super().__init__(reader,writer,timeout=timeout,greeting_host=greeting_host)
        self._mailCenter=mailCenter
        self._do_reset()

    def _do_reset(self):
        self._mailFrom=None
        self._prevMail=None
        self._rcpt=set()

    async def on_reset(self):
        self._do_reset()

    async def set_src(self,src_addr):
        uid=await self._mailCenter.get_uid_from_addr(src_addr)
        if uid is None:
            return False
        self._mailFrom=uid
        return True

    async def add_rcpt(self,addr):
        uid=await self._mailCenter.get_uid_from_addr(addr)
        if uid is None:
            return False
        self._rcpt.add(uid)
        return True

    async def on_data(self,msg):
        self.logger.error(self._mailFrom)
        self.logger.error(self._rcpt)
        self.logger.error(msg)


class SMTPServer(TCPServer):
    def __init__(self,config):
        server_config=config['mail']['smtp']
        self.__mailCenter=MailCenter.get_instance()
        self.__timeout=server_config.get('timeout',60)
        self.__greeting_host=config.get('greeting_host','')
        super().__init__(server_config['port'],
            host=server_config.get('host','127.0.0.1'),
            max_conn=server_config.get('max_connection',None))

    async def handler(self,reader,writer):
        smtphandler=SMTPHandler(MailCenter.get_instance(),
                                reader,writer,timeout=self.__timeout,
                                greeting_host=self.__greeting_host)
        await smtphandler.run()

