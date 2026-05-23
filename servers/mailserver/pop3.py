import asyncio
import re
import email
from email.message import Message
from email.header import Header
from email.utils import formatdate, format_datetime, localtime
from util import Logger
from util.tcpserver import TCPServer
from mailcenter import MailCenter


class POP3Error(Exception):
    pass


class POP3HandlerBase(Logger):
    _noAuthCmd={'USER','PASS'}
    def __init__(self,reader,writer,*,timeout=60):
        self._handlerDict={
            'USER':self._handleUser,
            'PASS':self._handlePass,
            'UIDL':self._handleUidl,
            'LIST':self._handleList,
            'STAT':self._handleStat,
            'RETR':self._handleRetr,
            'DELE':self._handleDel,
            'NOOP':self._handleNoop,
            'QUIT':self._handleQuit,
        }
        self._running=True
        self._uid=None
        self._user=None
        self._mailList=None
        self._reader=reader
        self._writer=writer
        self._timeout=timeout
        self._delSet=set()

    @staticmethod
    def _getCmd(line):
        if line==b'':
            return None
        cmd=line.decode('iso8859-1','ignore').strip().split()
        if not cmd:
            return None,None
        return cmd[0],cmd[1:]

    async def _readline(self):
        line=b''
        try:
            line=await asyncio.wait_for(self._reader.readuntil(b'\n'),
                                        timeout=self._timeout)
        except asyncio.exceptions.IncompleteReadError:
            self.logger.debug(f'Unexpected EOF')
        except asyncio.TimeoutError:
            self.logger.debug(f'Timeout')
        return line
    
    def _getMail(self,idx):
        try:
            if idx is None:
                raise POP3Error('Missing email num')
            idx=int(idx)-1
            if idx<0 or idx>=len(self._mailList):
                raise IndexError
            mail_id,msg=self._mailList[idx]
            return mail_id,msg
        except (ValueError,TypeError):
            raise POP3Error('Invalid email num')
        except IndexError:
            raise POP3Error('Mail not found')

    async def _handleUser(self,user=None):
        if user is None:
            raise POP3Error('Missing Username')
        self._user=user
        self._mailList=None
        self._delSet.clear()
    
    async def _handlePass(self,password=None):
        if password is None:
            raise POP3Error('Missing Password')
        if not await self.auth(self._user, password):
            raise POP3Error('Auth Failed')
        self._mailList=await self.mail_recv()
        
    async def _handleStat(self):
        mailCount=len(self._mailList)
        totalSize=sum([len(msg) for mail_id,msg in self._mailList])
        return f"{mailCount} {totalSize}"

    async def _handleRetr(self,idx=None):
        mail_id,msg=self._getMail(idx)
        return b'\r\n'+msg+b'\r\n.'
    
    async def _handleDel(self,idx=None):
        mail_id,msg=self._getMail(idx)
        self._delSet.add(mail_id)
        return b'\r\n'+msg+b'\r\n.'

    async def _handleUidl(self,idx=None):
        mail_id,msg=self._getMail(idx)
        return str(mail_id)

    async def _handleList(self,idx=None):
        content=line.decode('iso8859-1','ignore').strip()
        match=re.search(r'^[^\s]+\s+([^\s]+)',content)
        if idx is None:
            mail_count=len(self._mailList)
            totalSize=sum([len(msg) for mail_id,msg in self._mailList])
            res=f'{mail_count} messages ({totalSize} bytes)'
            for idx,(mail_id,msg) in enumerate(self._mailList):
                msg_size=len(msg)
                res+=f'\r\n{idx+1} {msg_size}'
            res+='\r\n.'
            return res
        else:
            mail_id,msg=self._getMail(idx)
            return f'{idx} {len(msg)}'

    async def _handleNoop(self):
        pass

    async def _handleQuit(self):
        self._running=False
        
    async def run(self):
        self._writer.write(b'+OK\r\n')
        while self._running:
            line=await self._readline()
            if line==b'':
                break
            try:
                cmd,param=self.__class__._getCmd(line)
                handler=self._handlerDict.get(cmd,None)
                if handler is None:
                    self.logger.debug(f'POP3 unhandled command:{line}')
                    raise POP3Error('Invalid Command')
                elif (cmd not in self._noAuthCmd) and (self._mailList is None):
                    raise POP3Error('Not Authorized')
                res=await handler(*param)
                if res is True or res is None:
                    res=b''
                elif isinstance(res,str):
                    res=f' {res}'.encode('iso8859-1')
                self._writer.write(b'+OK'+res+b'\r\n')
            except POP3Error as e:
                self._writer.write(f'-ERR {e.message}\r\n'.encode('iso8859-1'))
            finally:
                await self._writer.drain()
        await self.mail_delete(self._delSet)
        self._delSet.clear()

    async def auth(self):
        raise NotImplementedError("auth() unimplemented")

    async def mail_recv(self):
        raise NotImplementedError("mail_recv() unimplemented")

    async def mail_delete(self,del_set):
        pass


class POP3Handler(POP3HandlerBase):
    def __init__(self,mailCenter,reader,writer,*,timeout=60):
        super().__init__(reader,writer,timeout=timeout)
        self._mailCenter=mailCenter
        self._uid=None

    async def auth(self,username,password):
        self._uid=await self._mailCenter.auth(username,password)
        return self._uid is not None

    async def mail_recv(self):
        return []

    async def mail_delete(self,del_set):
        pass


class POP3Server(TCPServer):
    def __init__(self,config):
        server_config=config['mail']['pop3']
        self._timeout=server_config.get('timeout',60)
        super().__init__(server_config['port'],
            host=server_config.get('host','127.0.0.1'),
            max_conn=server_config.get('max_connection',None))

    async def handler(self,reader,writer):
        pop3handler=POP3Handler(MailCenter.get_instance(),
                                reader,writer,timeout=self._timeout)
        await pop3handler.run()

