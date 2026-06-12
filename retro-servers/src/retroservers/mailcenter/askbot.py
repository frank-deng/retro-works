import asyncio
import re
import json
import aiohttp
from .mailcenter import MailUserRobot


class MailUserRobotAI(MailUserRobot):
    def __init__(self,mailCenter,config):
        super().__init__(mailCenter,config)
        self._headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer '+self._config['api_key']
        }
        if 'model' not in self._config:
            raise ValueError('Model required')
        self._jsonBase={
            "stream":False,
            **self._config
        }
        self._url=self._config['url']
        for key in ('uid','username','module','url','api_key'):
            self._jsonBase.pop(key,None)

    async def _get_user_type(self,uid):
        res='user'
        if self._MailCenter.is_robot(uid):
            res='assistant'
        return res

    async def _get_conversation(self,email_list):
        last_user_type=None
        res=[]
        for email in reversed(email_list):
            uid,subject,body,extra=email['from_uid'],email['subject'],email['body'],email.get('extra')
            if re.match(r'^(Re:|Fwd:)',subject,re.IGNORECASE):
                subject=''
            else:
                subject+='\n'
            user_type=await self._get_user_type(uid)
            if last_user_type is None or user_type!=last_user_type:
                last_user_type=user_type
                res.append({
                    'role':user_type,
                    'content':f'{subject}{body}',
                    'reasoning_content':extra
                })
            else:
                res[-1]['content']+='\n'+f'{subject}{body}'
        return res

    async def _handler(self,email_id):
        uid=self._uid
        email_detail=await self._MailCenter.mail_detail(uid,email_id)
        if not email_detail:
            return
        messages=await self._get_conversation(email_detail)
        jsonData={
            **self._jsonBase,
            "messages": messages,
        }
        msg=None
        async with aiohttp.ClientSession() as session:
            async with session.post(self._url,headers=self._headers,
                                    json=jsonData) as response:
                res=json.loads(await response.text())
                msg=res['choices'][0]['message']
        body,extra=msg['content'],msg['reasoning_content']
        email=email_detail[0]
        subject='Re: '+re.sub(r'^(Re|Fwd):\s*','',email['subject'],1,re.IGNORECASE)
        await self._MailCenter.send(uid,[email['from_uid']],[],
                                    subject,body,email_id,extra=extra)
        await self._MailCenter.mark_read(uid,email_id)

