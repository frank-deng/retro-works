import asyncio,hashlib,os,re,importlib
from uuid import uuid4 as uuidgen
from util import Logger
from mailserver.pop3 import POP3Server
from mailserver.smtp import SMTPServer

class MailUserNormal(Logger):
    def __init__(self,userName,params):
        self.__user=userName
        self.__mailList=[]
        self.__hosts=set(params['hosts'])
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

    def checkHosts(self, hostIn):
        return hostIn in self.__hosts


class MailUserRobot(Logger):
    __task=None
    def __init__(self,userName,params,sendQueue):
        self.__user=userName
        self.__recvQueue=asyncio.Queue()
        self.__module=importlib.import_module(params['module'])
        self.__task=asyncio.create_task(self.__module.run(self.__user,params,self.__recvQueue,sendQueue))

    async def append(self,userFrom,msg):
        self.__recvQueue.put_nowait({
            'id':str(uuidgen()),
            'from':userFrom,
            'msg':msg,
        })

    def close(self):
        if self.__task is not None:
            self.__task.cancel()


class MailCenter(Logger):
    __task=None
    def __init__(self,config):
        self.__user={}
        self.__password={}
        self.__sendQueue=asyncio.Queue()
        userData=config['user']
        for userName in userData:
            userDetail=userData[userName]
            if 'password' in userDetail:
                self.__user[userName]=MailUserNormal(userName,userDetail.copy())
                self.__password[userName]=userDetail['password']
            elif 'module' in userDetail:
                self.__user[userName]=MailUserRobot(userName,
                        userDetail.copy(),self.__sendQueue)
        
    async def __sendQueueTask(self):
        try:
            while True:
                mail=await self.__sendQueue.get()
                target=mail.get('to',None)
                if (target is None) or (target not in self.__user):
                    continue
                await self.__user[target].append(mail.get('from','unknown'), mail['msg'])
        except asyncio.CancelledError:
            pass

    async def __aenter__(self):
        self.__task=asyncio.create_task(self.__sendQueueTask())

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        for user in self.__user.values():
            if isinstance(user,MailUserRobot):
                user.close()
        if self.__task is not None:
            self.__task.cancel()
            await self.__task

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
        userObj = self.__user.get(addr, self.__user.get(user, None))
        if userObj is None:
            return None
        elif isinstance(userObj, MailUserNormal) and not userObj.checkHosts(host):
            return None
        elif isinstance(userObj, MailUserNormal):
            return user
        else:
            return addr
    
    async def sendTo(self,userFrom,userTo,msg):
        if userTo not in self.__user:
            return False
        await self.__user[userTo].append(userFrom,msg)


class MailServer(MailCenter):
    def __init__(self,config):
        config=config['mail']
        super().__init__(config)
        self.__pop3Server=POP3Server(self,config)
        self.__smtpServer=SMTPServer(self,config)

    async def __aenter__(self):
        await super().__aenter__()
        await asyncio.gather(
            self.__pop3Server.__aenter__(),
            self.__smtpServer.__aenter__(),
            return_exceptions=True)

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        try:
            await asyncio.gather(
                self.__pop3Server.__aexit__(exc_type,exc_val,exc_tb),
                self.__smtpServer.__aexit__(exc_type,exc_val,exc_tb),
                return_exceptions=True)
        finally:
            await super().__aexit__(exc_type,exc_val,exc_tb)

    def close(self):
        self.__pop3Server.close()
        self.__smtpServer.close()

