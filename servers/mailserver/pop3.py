import asyncio
import re
from util import Logger
from util.tcpserver import TCPServer


class POP3Handler(Logger):
    __user=None
    __mailList=None
    __running=True
    __noAuthCmd={'USER','PASS'}
    def __init__(self,mailCenter,reader,writer,*,timeout=60):
        self.__mailCenter=mailCenter
        self.__reader=reader
        self.__writer=writer
        self.__timeout=timeout
        self.__delSet=set()
        self.__handlerDict={
            'USER':self.__handleUser,
            'PASS':self.__handlePass,
            'UIDL':self.__handleUidl,
            'LIST':self.__handleList,
            'STAT':self.__handleStat,
            'RETR':self.__handleRetr,
            'DELE':self.__handleDel,
            'NOOP':self.__handleNoop,
            'QUIT':self.__handleQuit,
        }
        
    async def __handleUser(self,line):
        content=line.decode('iso8859-1','ignore').strip()
        match=re.search(r'^[^\s]+\s+([^\s]+)',content)
        if match is None:
            self.__writer.write(b'-ERR Missing Username\r\n')
            return
        self.__user=match[1]
        self.__mailBox=None
        self.__mailList=None
        self.__delSet.clear()
        self.__writer.write(b'+OK\r\n')
    
    async def __handlePass(self,line):
        content=line.decode('iso8859-1','ignore').strip()
        match=re.search(r'^[^\s]+\s+([^\s]+)',content)
        if match is None:
            self.__writer.write(b'-ERR Missing Password\r\n')
            return
        self.__mailBox=self.__mailCenter.getUser(self.__user, match[1])
        if self.__mailBox is None:
            self.__writer.write(b'-ERR Auth Failed\r\n')
            return
        self.__mailList=await self.__mailBox.getAll()
        self.__writer.write(b'+OK\r\n')
        
    async def __handleStat(self,line):
        mailCount=len(self.__mailList)
        totalSize=0
        for item in self.__mailList:
            totalSize+=len(item['msg'])
        self.__writer.write(f"+OK {mailCount} {totalSize}\r\n".encode('iso8859-1'))

    async def __handleRetr(self,line):
        content=line.decode('iso8859-1','ignore').strip()
        match=re.search(r'^[^\s]+\s+([^\s]+)',content)
        if match is None:
            self.__writer.write(b'-ERR Missing email num\r\n')
            return
        idx=int(match[1])-1
        if idx<0 or idx>=len(self.__mailList):
            self.__writer.write(b'-ERR Mail not found\r\n')
            return
        msg=self.__mailList[idx]['msg']
        if re.search(rb'\r\n$',msg) is None:
            msg+=b'\r\n'
        msg+=b'.\r\n'
        self.__writer.write(b'+OK\r\n')
        self.__writer.write(msg)
    
    async def __handleDel(self,line):
        content=line.decode('iso8859-1','ignore').strip()
        match=re.search(r'^[^\s]+\s+([^\s]+)',content)
        if match is None:
            self.__writer.write(b'-ERR Missing email num\r\n')
            return
        idx=int(match[1])-1
        try:
            self.__delSet.add(self.__mailList[idx]['id'])
            self.__writer.write(b'+OK\r\n')
        except IndexError:
            self.__writer.write(b'-ERR Failed to delete mail\r\n')

    async def __handleUidl(self, line):
        content=line.decode('iso8859-1','ignore').strip()
        match=re.search(r'^[^\s]+\s+([^\s]+)',content)
        if match is None:
            self.__writer.write(b'-ERR Missing email num\r\n')
            return
        idx=int(match[1])-1
        try:
            mailid=self.__mailList[idx]['id']
            self.__writer.write(f'+OK {mailid}\r\n'.encode('iso8859-1'))
        except IndexError:
            self.__writer.write(b'-ERR Failed to get mail\r\n')

    async def __handleList(self, line):
        content=line.decode('iso8859-1','ignore').strip()
        match=re.search(r'^[^\s]+\s+([^\s]+)',content)
        if match is None:
            mail_count=len(self.__mailList)
            size_total=0
            for item in self.__mailList:
                size_total+=len(item['msg'])
            self.__writer.write(f'+OK {mail_count} messages ({size_total} bytes)\r\n'.encode('iso8859-1'))
            for idx in range(len(self.__mailList)):
                msg_size=len(self.__mailList[idx]['msg'])
                self.__writer.write(f'{idx+1} {msg_size}\r\n'.encode('iso8859-1'))
            self.__writer.write(b'.\r\n')
        else:
            idx=int(match[1])-1
            try:
                msg_size=len(self.__mailList[idx]['msg'])
                self.__writer.write(f'+OK {idx} {msg_size}\r\n'.encode('iso8859-1'))
            except IndexError:
                self.__writer.write(b'-ERR Failed to get mail\r\n')

    async def __handleNoop(self,line):
        self.__writer.write(b'+OK\r\n')

    async def __handleQuit(self,line):
        self.__running=False
        self.__writer.write(b'+OK\r\n')
        
    def __getCmd(self,line):
        if line==b'':
            return None
        cmd=line.decode('iso8859-1','ignore').strip()
        match=re.search(r'^([^\s]+)',cmd)
        if match is None:
            return ''
        return match[1]
    
    async def run(self):
        self.__writer.write(b'+OK\r\n')
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
                self.__writer.write(b'-ERR Invalid Command\r\n')
                self.logger.debug(f'POP3 unhandled command:{line}')
            elif (cmd not in self.__noAuthCmd) and (self.__mailList is None):
                self.__writer.write(b'-ERR Not Authorized\r\n')
            else:
                await handler(line)
            await self.__writer.drain()
        await self.__mailBox.delete(self.__delSet)
        self.__delSet.clear()


class POP3Server(TCPServer):
    __timeout=60
    def __init__(self,mailCenter,config):
        server_config=config['pop3']
        self.__mailCenter=mailCenter
        self.__timeout=server_config.get('timeout',60)
        super().__init__(server_config['port'],
            host=server_config.get('host','0,0,0,0'),
            max_conn=server_config.get('max_connection',None))

    async def handler(self,reader,writer):
        pop3handler=POP3Handler(self.__mailCenter,
                                reader,writer,timeout=self.__timeout)
        await pop3handler.run()

