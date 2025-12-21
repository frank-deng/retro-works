#!/usr/bin/env python3
#-*- coding:utf-8-*

import asyncio,json,os,sys,re,subprocess
import aiohttp

async def deepseek(question):
    deepseek_key=os.environ.get('DEEPSEEK_KEY')
    if not deepseek_key:
        raise KeyError('DEEPSEEK_KEY not set yet.')
    headers={
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer '+deepseek_key
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
        async with session.post('https://api.deepseek.com/chat/completions',headers=headers,json=jsonData,timeout=aiohttp.ClientTimeout(total=300)) as response:
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
        asyncio.run(deepseek(content))
        return 0
    except BrokenPipeError:
        pass
    except KeyboardInterrupt:
        pass
    except KeyError as e:
        print(e,file=sys.stderr)
        return 1

if '__main__'==__name__:
    exit(main())

