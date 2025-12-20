import aiohttp,asyncio,json,re,os
from typing import ClassVar
from mailserver import MailUserRobot
from datetime import datetime
import email
from email.message import Message
from email.header import Header
from uuid import uuid4 as uuidgen

class MailUserRobotAI(MailUserRobot):
    CHARSET_ALIAS:ClassVar[dict]={
        'cn-gb':'gb2312'
    }

    @staticmethod
    def __msg_get_data(msg):
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
        charset=MailUserRobotAI.CHARSET_ALIAS.get(charset,charset)
        subject,subjectCharset=email.header.decode_header(msg['Subject'])[0]
        if subjectCharset is None:
            subjectCharset=charset
        subjectCharset=MailUserRobotAI.CHARSET_ALIAS.get(subjectCharset,subjectCharset)
        if isinstance(subject,bytes):
            subject=subject.decode(subjectCharset)
        elif 'hz-gb-2312'==charset:
            subject=subject.encode('ascii').decode(subjectCharset)
        subject=subject.strip()
        payload=payload.decode(charset,errors='ignore')
        return subject,payload

    @staticmethod
    def __parse_content(remain):
        def __parse_content_part(text):
            cur=''
            remainder=''
            isReply=True
            for line in text.split('\n'):
                line=line.rstrip()
                if re.match(r'^[\-]{8,}$',line):
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

    def __save_result(self,content):
        now=datetime.now()
        date_str=now.strftime("%Y%m%d_%H%M%S")
        filename=f"{self.__class__.__name__}_{date_str}_{now.microsecond}.json"
        path=f"{self._params['storage_dir']}{os.sep}{filename}"
        with open(path,"w") as fp:
            fp.write(content)

    @staticmethod
    def __msg_apply_reply(text,textOrig):
        marker='> '
        res=f"{text.rstrip()}\n\n----------"
        for line in textOrig.rstrip().split('\n'):
            res+=f"\n{marker}{line.rstrip()}"
        return res.replace('\r','').replace('\n','\r\n')

    async def apiHandler(self,conversation):
        raise NotImplementedError('apiHandler must be implemented for calling external API.');

    async def __taskMain(self,userFrom,msg):
        msg=email.message_from_bytes(msg)
        subject,content=self.__class__.__msg_get_data(msg)
        conversation=self.__class__.__parse_content(content)
        content=self.__class__.__msg_apply_reply(await self.apiHandler(conversation), content)
        self.__save_result(content)
        reply_charset='HZ-GB-2312'
        msg_reply = Message()
        msg_reply['From']=self._user
        msg_reply['To']=msg['From']
        if re.match(r'Re:\s+', subject):
            msg_reply['Subject']=Header(subject, reply_charset)
        else:
            msg_reply['Subject']=Header("Re: "+subject, reply_charset)
        content_gb2312=content.encode('gb2312','replace')
        msg_reply.set_payload(content_gb2312.decode('gb2312'), charset=reply_charset)
        msg_reply_data=msg_reply.as_bytes().replace(b'\n',b'\r\n')
        await self.send(userFrom,msg_reply_data)
    
    async def __task(self,taskId,userFrom,msg):
        try:
            await self.__taskMain(userFrom,msg)
        except Exception as e:
            self.logger.error(e,exc_info=True)
        try:
            del self.__tasks[taskId]
        except Exception as e:
            self.logger.error(e,exc_info=True)

    def __init__(self,mailCenter,userName,params):
        super().__init__(mailCenter,userName,params)
        self.__tasks={}

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        try:
            for task in self.__tasks.values():
                try:
                    task.cancel()
                except Exception as e:
                    logger.error(e,exc_info=True)
        except Exception as e:
            logger.error(e,exc_info=True)

    async def append(self,userFrom,msg):
        taskId=str(uuidgen())
        self.__tasks[taskId]=asyncio.create_task(self.__task(taskId,userFrom,msg))

class MailUserRobotDeepseek(MailUserRobotAI):
    async def apiHandler(self,content):
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer '+self._params['deepseek_key']
        }
        messages=[]
        for i in range(len(content)):
            if ((i % 1) == 0):
                messages.append({
                        'role':'user',
                        'content':content[i],
                })
            else:
                messages.append({
                        'role':'assistant',
                        'content':content[i],
                })
        jsonData={
            "model": "deepseek-chat",
            "stream": False,
            "temperature": 0,
            "messages": messages,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.deepseek.com/chat/completions',headers=headers,json=jsonData) as response:
                res=json.loads(await response.text())
                return res['choices'][0]['message']['content']
        return None

class MailUserRobotErine(MailUserRobotAI):
    @staticmethod
    async def __getAccessToken(client_id,client_secret):
        url='https://aip.baidubce.com/oauth/2.0/token'
        data={
            'grant_type':'client_credentials',
            'client_id':client_id,
            'client_secret':client_secret
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url,data=data) as response:
                res=json.loads(await response.text())
                if res is not None and 'access_token' in res:
                    return res['access_token']
        return None
    
    async def apiHandler(self,content):
        access_token=await self.__class__.__getAccessToken(self._params['client_id'],self._params['client_secret'])
        if access_token is None:
            return None
        url=f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token={access_token}"
        messages=[]
        for i in range(len(content)):
            if ((i % 1) == 0):
                messages.append({
                        'role':'user',
                        'content':content[i],
                })
            else:
                messages.append({
                        'role':'assistant',
                        'content':content[i],
                })
        jsonData={
            'messages':messages,
            'temperature':0.01,
            'top_p':0,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url,json=jsonData) as response:
                res=json.loads(await response.text())
                return res.get('result',None)
        return None

