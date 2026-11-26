#!/usr/bin/env python3
#-*- coding:utf-8-*

import asyncio,json,os,sys,re,subprocess
import aiohttp
import click

FILE_MARKER='# AI Conversation History V1'

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
            if sys.stdout.isatty():
                try:
                    cmd=os.environ.get('VIEWER','less -FRX').split()
                    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
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
        for idx,content in enumerate(dialogue):
            role='user'
            if idx&1:
                role='assistant'
            jsonData['messages'].append({
                'role':role,
                'content':content
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
        
        for idx,content in enumerate(dialogue):
            role='user'
            if idx&1:
                role='assistant'
            jsonData['messages'].append({
                'role':role,
                'content':content,
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


def parse_file(fpath,question):
    new_file=False
    if not os.path.exists(fpath):
        with open(fpath,'w',encoding='utf8') as fp:
            fp.write(FILE_MARKER+'\n'+question+'\n')
        if sys.stdout.isatty() and sys.stdin.isatty():
            cmd=os.environ.get('EDITOR','vim').split()
            cmd.append(fpath)
            proc=subprocess.Popen(cmd)
            if proc is None:
                raise RuntimeError('Failed to launch editor.')
            proc.wait()
        new_file=True
    elif not os.path.isfile(fpath):
        raise FileNotFoundError(f'{fpath} not a file.')

    res=[]
    isQuestion=True
    with open(fpath,'r',encoding='utf8') as fp:
        marker=fp.readline().rstrip('\n\r')
        if marker!=FILE_MARKER:
            raise ValueError('File format mismatch.')
        content=''
        for line in fp:
            if isQuestion and re.match(r'^[-]{40,}\r?\n$',line):
                res.append(content.strip('\n\r'))
                content=''
                isQuestion=False
            elif not isQuestion and re.match(r'^[=]{40,}\r?\n$',line):
                res.append(content.strip('\n\r'))
                content=''
                isQuestion=True
            else:
                content+=line
        if content.strip():
            res.append(content.strip('\n\r'))

    if not new_file and question.strip():
        if (len(res)&1)==0:
            res.append(question)
        else:
            res[-1]=question+'\n'+res[-1]
    return res


def write_file(fpath,conversation):
    with open(fpath,'w',encoding='utf8') as fp:
        fp.write(FILE_MARKER+'\n')
        for idx,text in enumerate(conversation):
            fp.write(text.rstrip('\n\r')+'\n')
            if idx&1:
                fp.write('='*50+'\n')
            else:
                fp.write('-'*50+'\n')


@click.command(context_settings={
    'help_option_names': ['-h', '--help', '-?'],
    'ignore_unknown_options': True,
    'show_default': False,
})
@click.option('--model', '-m', default='deepseek', show_default=True,
              help='Model to use (deepseek, erine, etc.)')
@click.argument('file', required=True)
@click.argument('question',nargs=-1,required=False)
def main(model,file,question):
    try:
        question=' '.join(question)+'\n\n'
        if not sys.stdin.isatty():
            for line in sys.stdin:
                question+=line
        question=question.rstrip('\n\r')
        dialogue=parse_file(file,question)
        if (len(dialogue)&1)==0:
            click.secho('Question not found.',fg='yellow',err=True)
            return 1
        if model not in MODELS:
            raise RuntimeError(f'Unsupported model "{model}".')
        write_file(file,dialogue)
        askBot=MODELS[model](file)
        asyncio.run(askBot.ask(dialogue))
        return 0
    except (BrokenPipeError,KeyboardInterrupt):
        return 0
    except (RuntimeError,KeyError,FileNotFoundError,ValueError) as e:
        click.secho(e,fg='red',err=True)
        return 1

if '__main__'==__name__:
    exit(main())

