import asyncio
import re
import json
import aiohttp
from mailcenter import MailUserRobot

class MailUserRobotDeepseek(MailUserRobot):
    async def _api_handler(self,content):
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer '+self._config['deepseek_key']
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
            async with session.post(
                    'https://api.deepseek.com/chat/completions',
                    headers=headers,json=jsonData) as response:
                res=json.loads(await response.text())
                return res['choices'][0]['message']['content']
        return None

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

