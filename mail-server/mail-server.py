#!/usr/bin/env python3

import asyncio,signal,json,hashlib,os,re,threading,importlib,platform
from uuid import uuid4 as uuidgen
from traceback import print_exc

class MailUserNormal:
    def __init__(self,userName):
        self.__user=userName
        self.__mailList=[]
        self.__lock=asyncio.Lock()

    async def getAll(self):
        res=[]
        async with self.__lock:
            res=self.__mailList[:]
        return res

    async def delete(self,delSet):
        async with self.__lock:
            self.__mailList[:]=[mail for mail in self.__mailList if mail['id'] not in delSet]

    async def append(self,userFrom,msg):
        async with self.__lock:
            self.__mailList.append({
                'id':str(uuidgen()),
                'from':userFrom,
                'msg':msg
            })

class MailUserRobot:
    __task=None
    def __init__(self,userName,params,sendQueue):
        self.__user=userName
        self.__recvQueue=asyncio.Queue()
        self.__module=importlib.import_module(params['module'])
        self.__task=asyncio.create_task(self.__module.run(params,self.__recvQueue,sendQueue))

    async def append(self,userFrom,msg):
        self.__recvQueue.put_nowait({
            'id':str(uuidgen()),
            'from':userFrom,
            'msg':msg,
        })

    def close(self):
        if self.__task is not None:
            self.__task.cancel()

class MailCenter:
    __acceptedHosts={'10.0.2.2'}
    __task=None
    def __init__(self):
        self.__user={}
        self.__password={}
        self.__sendQueue=asyncio.Queue()
        
    async def __sendQueueTask(self):
        while True:
            mail=await self.__sendQueue.get()
            target=mail.get('to',None)
            if (target is None) or (target not in self.__user):
                continue
            await self.__user[target].append(mail.get('from','unknown'), mail['msg'])

    async def load(self, configFile):
        with open(configFile, 'r') as f:
            jsonData=json.load(f)
            for userName in jsonData:
                userDetail=jsonData[userName]
                if 'password' in userDetail:
                    self.__user[userName]=MailUserNormal(userName)
                    self.__password[userName]=userDetail['password']
                elif 'module' in userDetail:
                    self.__user[userName]=MailUserRobot(userName,userDetail.copy(),self.__sendQueue)
            self.__task=asyncio.create_task(self.__sendQueueTask())
            await asyncio.sleep(0)

    def getUser(self,user,passwordIn):
        password=self.__password.get(user,None)
        if password is None:
           return None
        passwordInHash=hashlib.sha256(passwordIn.encode('iso8859-1')).hexdigest()
        if password != passwordInHash:
           return None
        return self.__user[user]
    
    def checkAddr(self,addr,isSender=False):
        match=re.search(r'^([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+)$',addr)
        if match is None:
            return None
        user,host = match[1],match[2]
        if (host not in self.__acceptedHosts) or (user not in self.__user):
            return None
        elif isSender and (user not in self.__password):
            return None
        else:
            return user
    
    async def sendTo(self,userFrom,userTo,msg):
        if userTo not in self.__user:
            return False
        await self.__user[userTo].append(userFrom,msg)

    def close(self):
        for user in self.__user.values():
            if isinstance(user,MailUserRobot):
                user.close()
        if self.__task is not None:
            self.__task.cancel()
        
mailCenter=MailCenter()

class POP3Service:
    __user=None
    __mailList=None
    __running=True
    __noAuthCmd={'USER','PASS'}
    def __init__(self,reader,writer,timeout=60):
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
        global mailCenter
        content=line.decode('iso8859-1','ignore').strip()
        match=re.search(r'^[^\s]+\s+([^\s]+)',content)
        if match is None:
            self.__writer.write(b'-ERR Missing Password\r\n')
            return
        self.__mailBox=mailCenter.getUser(self.__user, match[1])
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
                print('POP3 unhandled command:', line)
            elif (cmd not in self.__noAuthCmd) and (self.__mailList is None):
                self.__writer.write(b'-ERR Not Authorized\r\n')
            else:
                await handler(line)
            await self.__writer.drain()
        await self.__mailBox.delete(self.__delSet)
        self.__delSet.clear()

class SMTPService:
    __running=True
    __mailFrom=None
    def __init__(self,reader,writer,timeout=60):
        self.__reader=reader
        self.__writer=writer
        self.__timeout=timeout
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
        await self.__writer.drain()

    async def __handleSrc(self,line):
        global mailCenter
        content=line.decode('iso8859-1','ignore').strip()
        match=re.search(r'^MAIL From:\s*<([^<>\s]+)>',content,re.IGNORECASE)
        if match is None:
            self.__writer.write(b'501 Invalid Parameter\r\n')
            await self.__writer.drain()
            return
        user=mailCenter.checkAddr(match[1],True)
        if user is None:
            self.__writer.write(b'510 Invalid email address\r\n')
            await self.__writer.drain()
            return
        self.__mailFrom=user
        self.__writer.write(b'250 OK\r\n')
        await self.__writer.drain()

    async def __handleRcpt(self,line):
        content=line.decode('iso8859-1','ignore').strip()
        match=re.search(r'^RCPT To:\s*<([^<>\s]+)>',content,re.IGNORECASE)
        if match is None:
            self.__writer.write(b'501 Invalid Parameter\r\n')
            await self.__writer.drain()
            return
        user=mailCenter.checkAddr(match[1])
        if user is None:
            self.__writer.write(b'510 Invalid email address\r\n')
            await self.__writer.drain()
            return
        self.__rcpt.add(user)
        self.__writer.write(b'250 OK\r\n')
        await self.__writer.drain()
        
    async def __handleNoop(self,line):
        self.__writer.write(b'250 OK\r\n')
        await self.__writer.drain()

    async def __handleQuit(self,line):
        self.__running=False
        self.__writer.write(b'250 OK\r\n')
        await self.__writer.drain()
        
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
            tasks.append(mailCenter.sendTo(self.__mailFrom, user, msg))
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
        self.__writer.write(b'220 Email Server 10.0.2.2\r\n')
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
                print('SMTP unhandled command:', line)
                continue
            try:
                await handler(line)
            except Exception:
                print_exc()
                self.__writer.write(b'550 Internal Error\r\n')
                await self.__writer.drain()

async def service_handler_pop3(reader,writer):
    try:
        srv=POP3Service(reader,writer)
        await srv.run()
    except (asyncio.TimeoutError, ConnectionResetError, BrokenPipeError):
        pass
    except Exception as e:
        print_exc()
    finally:
        if not writer.is_closing():
            writer.close()
            await writer.wait_closed()

async def service_handler_smtp(reader,writer):
    try:
        srv=SMTPService(reader,writer)
        await srv.run()
    except (asyncio.TimeoutError, ConnectionResetError, BrokenPipeError):
        pass
    except Exception as e:
        print_exc()
    finally:
        if not writer.is_closing():
            writer.close()
            await writer.wait_closed()

server_pop3=None
server_smtp=None

def close_server(a,b):
    global server_pop3,server_smtp
    if server_pop3 is not None:
        server_pop3.close()
    if server_smtp is not None:
        server_smtp.close()

async def main(args):
    global mailCenter,server_pop3,server_smtp
    server_pop3,server_smtp,dummy = await asyncio.gather(
        asyncio.start_server(service_handler_pop3,host=args.host,port=args.port_pop3),
        asyncio.start_server(service_handler_smtp,host=args.host,port=args.port_smtp),
        mailCenter.load(args.config)
    )
    loop = asyncio.get_event_loop()
    for s in (signal.SIGINT, signal.SIGTERM):
        if 'Windows'==platform.system():
            signal.signal(s, close_server)
        else:
            loop.add_signal_handler(s, lambda:close_server(None,None))
    try:
        async with server_pop3:
            async with server_smtp:
                await asyncio.gather(server_pop3.serve_forever(), server_smtp.serve_forever())
    except (asyncio.exceptions.CancelledError, KeyboardInterrupt):
        pass
    except Exception as e:
        print_exc()
    finally:
        mailCenter.close()
        await asyncio.gather(server_pop3.wait_closed(), server_smtp.wait_closed())

if '__main__'==__name__:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host',
        help='Specify binding host for the e-mail server.',
        default=''
    )
    parser.add_argument(
        '--port_pop3',
        help='Specify port for the e-mail server.',
        type=int,
        default=110
    )
    parser.add_argument(
        '--port_smtp',
        help='Specify port for the e-mail server.',
        type=int,
        default=25
    )
    parser.add_argument(
        '--config',
        '-c',
        help='Specify config file for the e-mail server.',
        default='./mail-server.json'
    )
    args = parser.parse_args()
    asyncio.run(main(args))

