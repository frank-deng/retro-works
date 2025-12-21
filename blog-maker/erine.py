#!/usr/bin/env python3
#-*- coding:utf-8-*

import asyncio,signal,json,os,sys,readline,re,subprocess
import aiohttp

async def getAccessToken(client_id,client_secret):
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

async def askBot(access_token,question):
    url=f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token={access_token}"
    result=''
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
            proc=subprocess.Popen(['less','-FRX'],stdin=subprocess.PIPE)
            async for chunk in response.content:
                chunk_str=re.sub('^data: ', '', chunk.decode().strip())
                if not chunk_str:
                    continue
                data=json.loads(chunk_str).get('result')
                proc.stdin.write(data.encode('utf-8'))
                proc.stdin.flush()
            proc.stdin.close()
            proc.wait()

async def input_stdin():
    content=''
    if sys.stdin.isatty():
        print('请输入您的问题：')
    try:
        while True:
            line=input()
            line=line.strip()
            if line=='.':
                break
            else:
                content+=line+'\n'
    except EOFError:
        pass
    if sys.stdin.isatty():
        print('回答中……')
    return content

def process_content(template):
    content=[]
    stdin_processed=False
    for item in template:
        if item!='-':
            content.append(item)
        elif not stdin_processed:
            stdin_processed=True
            content.append('\n'.join(sys.stdin.readlines()))
    return '\n'.join(content)

async def main(args):
    client_id=os.environ.get('CLIENT_ID')
    client_secret=os.environ.get('CLIENT_SECRET')
    if (not client_id) or (not client_secret):
        print('Environ CLIENT_ID and CLIENT_SECRET not set yet.',file=sys.stderr)
        return
    access_token=await getAccessToken(os.environ.get('CLIENT_ID'),os.environ.get('CLIENT_SECRET'))
    content=''
    if len(args.question)==0:
        content=await input_stdin()
    else:
        content=process_content(args.question)
    sys.stdin.close()
    await askBot(access_token,content)

if '__main__'==__name__:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'question',
        nargs='*'
    )
    args = parser.parse_args();
    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        pass
    exit(0)

