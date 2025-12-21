#!/usr/bin/env python3
#-*- coding:utf-8-*

import asyncio,json,os,sys,re,subprocess
import aiohttp

class AskBot:
    async def _ondata(self,chunk):
        raise NotImplementedError('_ondata() method must be implemented')
        
    async def _handleResponse(self,response):
        target=sys.stdout.buffer
        proc=None
        if sys.stdout.isatty():
            try:
                proc=subprocess.Popen(['less','-FRX'],stdin=subprocess.PIPE)
                target=proc.stdin
            except Exception as e:
                print(e,file=sys.stderr)
        async for chunk in response.content:
            text=await self._ondata(chunk)
            if text is None:
                continue
            target.write(text.encode('utf-8'))
            target.flush()
        if proc is not None:
            proc.stdin.close()
            proc.wait()

    async def ask(self,question):
        raise NotImplementedError('ask() method must be implemented')


class AskBotDeepSeek(AskBot):
    def __init__(self):
        env_key='DEEPSEEK_KEY'
        self.__key=os.environ.get(env_key)
        if not self.__key:
            raise KeyError(f'Environ {env_key} not set.')
    
    async def _ondata(self, chunk):
        chunk_str=re.sub('^data: ', '', chunk.decode().strip())
        if not chunk_str or chunk_str == '[DONE]':
            return None
        data=json.loads(chunk_str)
        return data['choices'][0]['delta']['content']
        
    async def ask(self,question):
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer '+self.__key
        }
        jsonData={
            "model": "deepseek-chat",
            "top_p": 0.01,
            "stream": True,
            "messages": [
                {
                    'role':'user',
                    'content':question,
                }
            ],
        }
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.deepseek.com/chat/completions',
                                    headers=headers,
                                    json=jsonData,
                                    timeout=aiohttp.ClientTimeout(total=300)
                                    ) as response:
                await self._handleResponse(response)


class AskBotErine(AskBot):
    def __init__(self):
        env_key='ERINE_KEY'
        self.__key=os.environ.get(env_key)
        if not self.__key:
            raise KeyError(f'Environ {env_key} not set.')
    
    async def _ondata(self, chunk):
        chunk_str=re.sub('^data: ', '', chunk.decode().strip())
        if not chunk_str:
            return None
        return json.loads(chunk_str).get('result')
        
    async def ask(self,question):
        client_id,client_secret=self.__key.split(':')
        data={
            'grant_type':'client_credentials',
            'client_id':client_id,
            'client_secret':client_secret
        }
        access_token=None
        async with aiohttp.ClientSession() as session:
            async with session.post('https://aip.baidubce.com/oauth/2.0/token',data=data) as response:
                res=json.loads(await response.text())
                if res is not None and 'access_token' in res:
                    access_token=res['access_token']
        if access_token is None:
            raise RuntimeError('Failed to get access token.')
        url=f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token={access_token}"
        jsonData={
            'messages':[
                {
                    'role':'user',
                    'content':question,
                    'temperature':0.01,
                    'top_p':0,
                }
            ],
            'stream':True,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url,json=jsonData) as response:
                await self._handleResponse(response)


async def async_main(question):
    askBot=AskBotErine()
    await askBot.ask(question)

USAGE=f"""Usage:

{sys.argv[0]} question
{sys.argv[0]} <<< question
echo question | {sys.argv[0]}
{sys.argv[0]} < question.txt
cat question.txt | {sys.argv[0]}
"""

def main():
    content=''
    ishelp=False
    if len(sys.argv)==2 and sys.argv[1] in ('-?','-h','--help'):
        ishelp=True
    else:
        content=' '.join(sys.argv[1:])+'\n'
    if ishelp or (sys.stdin.isatty() and not content.strip()):
        print(USAGE,file=sys.stderr)
        exit(1)
    if not sys.stdin.isatty():
        try:
            while True:
                content+=input().strip()+'\n'
        except EOFError:
            pass
    try:
        asyncio.run(async_main(content))
        return 0
    except BrokenPipeError:
        pass
    except KeyboardInterrupt:
        pass
    except RuntimeError as e:
        print(e,file=sys.stderr)
        return 1
    except KeyError as e:
        print(e,file=sys.stderr)
        return 1

if '__main__'==__name__:
    exit(main())
