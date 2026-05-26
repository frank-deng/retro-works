import asyncio
import re
import json
import aiohttp
from retroservers.mailcenter import MailUserRobot


class MailUserRobotAI(MailUserRobot):
    async def _get_user_type(self,uid):
        res='user'
        if self._MailCenter.is_robot(uid):
            res='assistant'
        return res

    def _get_conversation(self,email_list):
        last_user_type=None
        res=[]
        for email in reversed(email_list):
            uid,subject,body=email['from_uid'],email['subject'],email['body']
            if re.match(r'^(Re:|Fwd:)',subject,re.IGNORECASE):
                subject=''
            else:
                subject+='\n'
            user_type=self._get_user_type(uid)
            if last_user_type is None or user_type!=last_user_type:
                last_user_type=user_type
                res.append(f'{subject}{body}')
            else:
                res[-1]+='\n'+f'{subject}{body}'
        return res

    async def _handler(self,email_id):
        uid=self._uid
        email_detail=await self._MailCenter.mail_detail(uid,email_id)
        if not email_detail:
            return
        conversation=self._get_conversation(email_detail)
        body=await self._api_handler(conversation)
        email=email_detail[0]
        subject='Re: '+re.sub(r'^(Re|Fwd):\s*','',email['subject'],1,re.IGNORECASE)
        await self._MailCenter.send(uid,[email['from_uid']],[],
                                    subject,body,email_id)
        await self._MailCenter.mark_read(uid,email_id)


class MailUserRobotDeepseek(MailUserRobotAI):
    async def _api_handler(self,content):
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer '+self._config['deepseek_key']
        }
        messages=[]
        for i in range(len(content)):
            if ((i % 1) == 0):
                messages.append({'role':'user','content':content[i]})
            else:
                messages.append({'role':'assistant','content':content[i]})
        jsonData={
            "model": "deepseek-chat",
            "stream": False,
            "temperature": 0,
            "messages": messages,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    'https://api.deepseek.com/chat/completions',
                    headers=headers,json=jsonData) as response:
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
    
    async def _api_handler(self,content):
        access_token=await self.__class__.__getAccessToken(
            self._config['client_id'],self._config['client_secret'])
        if access_token is None:
            return None
        url=f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token={access_token}"
        messages=[]
        for i in range(len(content)):
            if ((i % 1) == 0):
                messages.append({'role':'user','content':content[i]})
            else:
                messages.append({'role':'assistant','content':content[i]})
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

