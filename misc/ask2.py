#!/usr/bin/env python3
#-*- coding:utf-8-*

import asyncio,signal,json,os,sys,readline,re,subprocess
import aiohttp

async def askBot(deepseek_key, question):
    headers={
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer '+deepseek_key
    }
    jsonData={
        "model": "deepseek-chat",
        "stream": False,
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
        async with session.post('https://api.deepseek.com/chat/completions',headers=headers,json=jsonData) as response:
            proc=subprocess.Popen(['less','-FRX'],stdin=subprocess.PIPE)
            async for chunk in response.content:
                chunk_str=re.sub('^data: ', '', chunk.decode().strip())
                if not chunk_str or chunk_str == '[DONE]':
                    continue
                data=json.loads(chunk_str)
                text = data['choices'][0]['delta']['content']
                proc.stdin.write(text.encode('utf-8'))
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
    deepseek_key=os.environ.get('DEEPSEEK_KEY')
    if not deepseek_key:
        print('DEEPSEEK_KEY not set yet.',file=sys.stderr)
        return
    content=''
    if len(args.question)==0:
        content=await input_stdin()
    else:
        content=process_content(args.question)
    sys.stdin.close()
    await askBot(deepseek_key,content)

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

