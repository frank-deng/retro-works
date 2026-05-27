from typing import ClassVar
import asyncio
import re
import email
from email.header import decode_header
from email.utils import getaddresses
from .util import Logger
from .util.tcpserver import TCPServer
from . import MailCenter


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
    @staticmethod
    def _parse_content(remain):
        def __parse_content_part(text):
            cur=''
            remainder=''
            isReply=True
            for line in text.split('\n'):
                line=line.rstrip()
                if re.match(r'^([\-]{8,}|At.*, you wrote:.*)$',line,re.IGNORECASE):
                    isReply=False
                elif isReply:
                    cur+=line+'\n'
                else:
                    remainder+=re.sub(r'^[\:\|\>]\s?','',line,count=1)+'\n'
            return cur,remainder
        res=[]
        while True:
            text,remain=__parse_content_part(remain)
            res.append(text)
            if not remain:
                break
        res.reverse()
        return res

    def __init__(self,mailCenter,encoding,reader,writer,*,timeout=60,
                 greeting_host=''):
        super().__init__(reader,writer,timeout=timeout,greeting_host=greeting_host)
        self._encoding=encoding
        self._mailCenter=mailCenter
        self._do_reset()

    def _parse_header(self,header):
        if header is None:
            return ''
        if isinstance(header,str):
            return header
        parts=[]
        for part,encoding in decode_header(header):
            if not isinstance(part,bytes):
                parts.append(part)
                continue
            try:
                encoding=encoding.lower()
                if 'hz-gb-2312'==encoding:
                    part=part.encode('ascii',errors='ignore')
                parts.append(part.decode(encoding,errors='ignore'))
            except LookupError:
                parts.append(part.decode(self._encoding,errors='ignore'))
        return ''.join(parts)

    def _msg_get_data(self,msg):
        charset=None
        payload=None
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() in {'text/plain','text/html'}:
                    charset=part.get_content_charset()
                    payload=part.get_payload(decode=True)
                    break
        else:
            charset=msg.get_content_charset()
            payload=msg.get_payload(decode=True)
        subject=self._parse_header(msg['Subject']).strip()
        try:
            payload=payload.decode(charset,errors='ignore')
        except LookupError:
            payload=payload.decode(self._encoding,errors='ignore')
        return subject,payload

    def _do_reset(self):
        self._mailFrom=None
        self._prevMail=None
        self._rcpt={}

    async def on_reset(self):
        self._do_reset()

    async def set_src(self,src_addr):
        uid,_=await self._mailCenter.get_uid_from_addr(src_addr)
        if uid is None:
            return False
        self._mailFrom=uid
        return True

    async def add_rcpt(self,addr):
        uid,_=await self._mailCenter.get_uid_from_addr(addr)
        if uid is None:
            return False
        if uid not in self._rcpt:
            self._rcpt[uid]=addr
        return True

    async def on_data(self,msg):
        msg=email.message_from_bytes(msg)
        reply_to,prev_email_id=msg['Reply-To'],None
        if reply_to is not None:
            _,prev_email_id=await self._mailCenter.get_uid_from_addr(reply_to)
        subject,content=self._msg_get_data(msg)
        to_dict,cc_dict={},{}
        for name,addr in getaddresses([self._parse_header(msg['To'])]):
            uid,_=await self._mailCenter.get_uid_from_addr(addr)
            if uid is None:
                continue
            to_dict[uid]=True
        for name,addr in getaddresses([self._parse_header(msg['Cc'])]):
            uid,_=await self._mailCenter.get_uid_from_addr(addr)
            if uid is None:
                continue
            cc_dict[uid]=True
        to,cc=[],[]
        for uid in self._rcpt:
            if uid in to_dict:
                to.append(uid)
            elif uid in cc_dict:
                cc.append(uid)
            else:
                to.append(uid)
        content=(__class__._parse_content(content))[-1]
        await self._mailCenter.send(self._mailFrom,to,cc,subject,content,prev_email_id)


class SMTPServer(TCPServer):
    def __init__(self,config):
        server_config=config['mail']['smtp']
        self._timeout=server_config.get('timeout',60)
        self._encoding=server_config.get('encoding','gbk')
        self._greeting_host=config['mail'].get('host','')
        super().__init__(server_config['port'],
            host=server_config.get('host','127.0.0.1'),
            max_conn=server_config.get('max_connection',None))

    async def handler(self,reader,writer):
        smtphandler=SMTPHandler(MailCenter.get_instance(),self._encoding,
                                reader,writer,timeout=self._timeout,
                                greeting_host=self._greeting_host)
        await smtphandler.run()

