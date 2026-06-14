import asyncio
import sys
import re
import email
import aiosmtpd
from aiosmtpd.smtp import SMTP
from email.header import decode_header
from email.utils import getaddresses
from .util import Logger
from . import MailCenter


class SMTPHandler(Logger):
    def __init__(self,mailCenter,encoding):
        super().__init__()
        self._mailCenter=mailCenter
        self._encoding=encoding

    async def handle_MAIL(self,server,session,envelope,address,mail_options):
        uid,_=await self._mailCenter.get_uid_from_addr(address)
        if uid is None:
            return '550 5.1.1 User unknown'
        if hasattr(envelope,'rcpt_uid') and uid in getattr(envelope,'rcpt_uid'):
            return '550 5.1.1 Sender cannot be the same as recipient'
        envelope.from_uid=uid
        envelope.mail_from=address
        return '250 OK'

    async def handle_RCPT(self,server,session,envelope,address,rcpt_options):
        uid,_=await self._mailCenter.get_uid_from_addr(address)
        if uid is None:
            return '550 5.1.1 User unknown'
        if uid==getattr(envelope,'from_uid',None):
            return '550 5.1.1 Recipient cannot be the same as sender'
        if not hasattr(envelope,'rcpt_uid'):
            envelope.rcpt_uid={}
        envelope.rcpt_uid[uid]=True
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self,server,session,envelope):
        msg=email.message_from_bytes(envelope.original_content)
        reply_to,prev_email_id=msg['Reply-To'],None
        if reply_to is not None:
            _,prev_email_id=await self._mailCenter.get_uid_from_addr(reply_to)
        from_uid=getattr(envelope,'from_uid',None)
        rcpt_uid=getattr(envelope,'rcpt_uid',{})
        if from_uid is None:
            return '550 5.1.0 Address rejected'
        to,cc={},{}
        for name,addr in getaddresses([self._parse_header(msg['To'])]):
            uid,_=await self._mailCenter.get_uid_from_addr(addr)
            if uid is None or uid not in rcpt_uid:
                continue
            to[uid]=True
        for name,addr in getaddresses([self._parse_header(msg['Cc'])]):
            uid,_=await self._mailCenter.get_uid_from_addr(addr)
            if uid is None or uid not in rcpt_uid or uid in to:
                continue
            cc[uid]=True
        to,cc=to.keys(),cc.keys()
        if not to and not cc:
            return '550 5.1.0 Address rejected'
        subject,content=self._msg_get_data(msg)
        content=(__class__._parse_content(content))[-1]
        await self._mailCenter.send(from_uid,to,cc,subject,content,prev_email_id)
        return '250 OK'

    @staticmethod
    def _parse_content(remain):
        def _parse_content_part(text):
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
            text,remain=_parse_content_part(remain)
            res.append(text)
            if not remain:
                break
        res.reverse()
        return res

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


class SMTPServer(Logger):
    def __init__(self,config):
        self._config=config['mail']['smtp']
        self._handler=SMTPHandler(MailCenter.get_instance(),
                                  self._config.get('encoding','gbk'))
        self._server=None

    async def __aenter__(self):
        reuse_port=True
        if 'win32'==sys.platform:
            reuse_port=None
        loop=asyncio.get_running_loop()
        self._server=await loop.create_server(lambda:SMTP(self._handler),
            host=self._config.get('host','127.0.0.1'),
            port=self._config.get('port',25),
            reuse_address=True,reuse_port=reuse_port
        )
        return self

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()

