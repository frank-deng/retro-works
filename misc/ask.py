#!/usr/bin/env python3
#-*- coding:utf-8-*

import asyncio,json,os,sys,re,subprocess
import aiohttp
import click

class AskBot:
    def __init__(self, outfile):
        self.__outfile=outfile
        
    async def _ondata(self,chunk):
        raise NotImplementedError('_ondata() method must be implemented')
        
    async def _handleResponse(self,response):
        target=sys.stdout.buffer
        proc=None
        fp=None
        try:
            fp=open(self.__outfile,'a',encoding='utf8')
            fp.write('\n'+('-'*50)+'\n')
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
                if fp is not None:
                    fp.write(text)
                    fp.flush()
            fp.write('\n'+('='*50)+'\n')
        except Exception as e:
            click.secho(e,fg='red',err=True)
        finally:
            if fp is not None:
                fp.close()
            if proc is not None:
                proc.stdin.close()
                proc.wait()

    async def ask(self,dialogue):
        raise NotImplementedError('ask() method must be implemented')


class AskBotDeepSeek(AskBot):
    def __init__(self, outfile):
        super().__init__(outfile)
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
        
    async def ask(self,dialogue):
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer '+self.__key
        }
        jsonData={
            "model": "deepseek-chat",
            "top_p": 0.01,
            "stream": True,
            "messages": [],
        }
        for idx in range(len(dialogue)):
            role='user'
            if idx&1:
                role='assistant'
            jsonData['messages'].append({
                'role':role,
                'content':dialogue[idx]
            })
        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.deepseek.com/chat/completions',
                                    headers=headers,
                                    json=jsonData,
                                    timeout=aiohttp.ClientTimeout(total=300)
                                    ) as response:
                await self._handleResponse(response)


class AskBotErine(AskBot):
    def __init__(self, outfile):
        super().__init__(outfile)
        env_key='ERINE_KEY'
        self.__key=os.environ.get(env_key)
        if not self.__key:
            raise KeyError(f'Environ {env_key} not set.')
    
    async def _ondata(self, chunk):
        chunk_str=re.sub('^data: ', '', chunk.decode().strip())
        if not chunk_str:
            return None
        return json.loads(chunk_str).get('result')
        
    async def ask(self,dialogue):
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
            'messages':[],
            'stream':True,
        }
        
        for idx in range(len(dialogue)):
            role='user'
            if idx&1:
                role='assistant'
            jsonData['messages'].append({
                'role':role,
                'content':dialogue[idx],
                'temperature':0.01,
                'top_p':0
            })
        async with aiohttp.ClientSession() as session:
            async with session.post(url,json=jsonData) as response:
                await self._handleResponse(response)


MODELS={
    'deepseek':AskBotDeepSeek,
    'erine':AskBotErine
}


def parse_file(fpath):
    if not os.path.isfile(fpath):
        raise FileNotFoundError(f'{fpath} not found or not a file.')
    res=[]
    question=True
    with open(fpath,'r',encoding='utf8') as fp:
        content=''
        for line in fp:
            if question and re.match(r'^[-]{40,}\r?\n$',line):
                res.append(content.strip())
                content=''
                question=False
            elif not question and re.match(r'^[=]{40,}\r?\n$',line):
                res.append(content.strip())
                content=''
                question=True
            else:
                content+=line
        content=content.strip()
        if content:
            res.append(content)
    return res


@click.command(context_settings={
    'help_option_names': ['-h', '--help', '-?'],
    'ignore_unknown_options': True
})
@click.option('--model', '-m', default='deepseek', show_default=True,
              help='Model to use (deepseek, erine, etc.)')
@click.argument('file', required=True)
@click.pass_context
def main(ctx,model,file):
    """For VIM users, use :!python ask.py %"""
    try:
        dialogue=parse_file(file)
        if (len(dialogue)&1)==0:
            click.secho('Question not found.',fg='yellow',err=True)
            ctx.exit(1)
        if model not in MODELS:
            raise RuntimeError(f'Unsupported model "{model}".')
        askBot=MODELS[model](file)
        asyncio.run(askBot.ask(dialogue))
    except BrokenPipeError:
        pass
    except KeyboardInterrupt:
        pass
    except RuntimeError as e:
        click.secho(e,fg='red',err=True)
        ctx.exit(1)
    except KeyError as e:
        click.secho(e,fg='red',err=True)
        ctx.exit(1)
    ctx.exit(0)

if '__main__'==__name__:
    main()

