import asyncio
import re
from util import Logger
from util.tcpserver import TCPServer


class SMTPHandler(Logger):
    __running=True
    __mailFrom=None
    def __init__(self,mailCenter,reader,writer,*,host='',timeout=60,
                 greeting_host='10.0.2.2'):
        self.__mailCenter=mailCenter
        self.__reader=reader
        self.__writer=writer
        self.__host=host
        self.__timeout=timeout
        self.__greeting_host=greeting_host
        self.__rcpt=set()
        self.__handlerDict={
            'HELO':self.__handleGreeting,
            'EHLO':self.__handleGreeting,
            'MAIL':self.__handleSrc,
            'RCPT':self.__handleRcpt,
            'DATA':self.__handleData,
            'NOOP':self.__handleNoop,
            'QUIT':self.__handleQuit,
            'RSET':self.__handleNoop,
        }

    async def __handleGreeting(self,line):
        self.__writer.write(b'250 OK\r\n')

    async def __handleSrc(self,line):
        content=line.decode('iso8859-1','ignore').strip()
        match=re.search(r'^MAIL From:\s*<([^<>\s]+)>',content,re.IGNORECASE)
        if match is None:
            self.__writer.write(b'501 Invalid Parameter\r\n')
            return
        user=self.__mailCenter.checkAddr(match[1],True)
        if user is None:
            self.__writer.write(b'510 Invalid email address\r\n')
            return
        self.__mailFrom=user
        self.__writer.write(b'250 OK\r\n')

    async def __handleRcpt(self,line):
        content=line.decode('iso8859-1','ignore').strip()
        match=re.search(r'^RCPT To:\s*<([^<>\s]+)>',content,re.IGNORECASE)
        if match is None:
            self.__writer.write(b'501 Invalid Parameter\r\n')
            return
        user=self.__mailCenter.checkAddr(match[1])
        if user is None:
            self.__writer.write(b'510 Invalid email address\r\n')
            return
        self.__rcpt.add(user)
        self.__writer.write(b'250 OK\r\n')
        
    async def __handleNoop(self,line):
        self.__writer.write(b'250 OK\r\n')

    async def __handleQuit(self,line):
        self.__running=False
        self.__writer.write(b'250 OK\r\n')
        
    async def __handleData(self,line):
        self.__writer.write(b'354 End data with <CR><LF>.<CR><LF>\r\n')
        await self.__writer.drain()
        msg=b''
        while msg.find(b'\r\n.\r\n')<0:
            msg+=await asyncio.wait_for(self.__reader.read(512), timeout=self.__timeout)
        msg=msg[:msg.find(b'\r\n.\r\n')]
        self.__writer.write(b'250 Mail OK\r\n')
        await self.__writer.drain()
        tasks=[]
        for user in self.__rcpt:
            tasks.append(self.__mailCenter.sendTo(self.__mailFrom, user, msg))
        await asyncio.gather(*tasks)

    def __getCmd(self,line):
        if line==b'':
            return None
        cmd=line.decode('iso8859-1','ignore').strip()
        match=re.search(r'^([^\s]+)',cmd)
        if match is None:
            return ''
        return match[1]
    
    async def run(self):
        self.__writer.write(f'220 Email Server {self.__greeting_host}\r\n'.encode('iso8859-1'))
        while self.__running:
            line=b''
            try:
                line=await asyncio.wait_for(self.__reader.readuntil(b'\n'), timeout=self.__timeout)
            except asyncio.exceptions.IncompleteReadError:
                continue
            cmd=self.__getCmd(line)
            if cmd is None:
                break
            handler=self.__handlerDict.get(cmd,None)
            if handler is None:
                self.__writer.write(b'502 Unimplemented Command\r\n')
                self.logger.debug(f'SMTP unhandled command:{line}')
                continue
            try:
                await handler(line)
            except Exception:
                self.__writer.write(b'550 Internal Error\r\n')
                raise
            finally:
                await self.__writer.drain()


class SMTPServer(TCPServer):
    __timeout=60
    def __init__(self,mailCenter,config):
        server_config=config['smtp']
        self.__mailCenter=mailCenter
        self.__timeout=server_config.get('timeout',60)
        self.__greeting_host=config.get('greeting_host','10.0.2.2')
        super().__init__(server_config['port'],
            host=server_config.get('host','0,0,0,0'),
            max_conn=server_config.get('max_connection',None))

    async def handler(self,reader,writer):
        smtphandler=SMTPHandler(self.__mailCenter,
                                reader,writer,timeout=self.__timeout,
                                greeting_host=self.__greeting_host)
        await smtphandler.run()

