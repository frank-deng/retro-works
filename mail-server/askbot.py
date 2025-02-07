import aiohttp,asyncio,json,sys
import email
from email.message import EmailMessage
from email.message import Message
from email.header import Header
from codecs import decode
import traceback,logging

CHARSET_ALIAS={
        'cn-gb':'gb2312'
}

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
    
async def ask_erine(params,question):
    key=params['erine_key']
    access_token=await getAccessToken(key[0],key[1])
    if access_token is None:
        return None
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
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url,json=jsonData) as response:
            res=json.loads(await response.text())
            return res.get('result',None)
    return None

async def ask_deepseek(params,question):
    headers={
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer '+params['deepseek_key']
    }
    jsonData={
        "model": "deepseek-chat",
        "stream": False,
        "temperature": 0,
        "messages": [
            {
                "role":"user",
                "content":question
            }
        ],
    }
    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.deepseek.com/chat/completions',headers=headers,json=jsonData) as response:
            res=json.loads(await response.text())
            return res['choices'][0]['message']['content']
    return None

def msg_get_data(msg):
    charset=None
    payload=None
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() in {'text/plain','text/html'}:
                charset=part.get_content_charset()
                payload=part.get_payload(decode=True)
    else:
        charset=msg.get_content_charset()
        payload=msg.get_payload(decode=True)
    charset=CHARSET_ALIAS.get(charset,charset)
    subject,subjectCharset=email.header.decode_header(msg['Subject'])[0]
    if subjectCharset is None:
        subjectCharset=charset
    subjectCharset=CHARSET_ALIAS.get(subjectCharset,subjectCharset)
    if isinstance(subject,bytes):
        subject=subject.decode(subjectCharset)
    elif 'hz-gb-2312'==charset:
        subject=subject.encode('ascii').decode(subjectCharset)
    subject=subject.strip()
    payload=payload.decode(charset,errors='ignore')
    return subject,payload

def msg_apply_reply(text,textOrig):
    marker='> '
    res=f"{text.rstrip()}\n\n----------"
    for line in textOrig.rstrip().split('\n'):
        res+=f"\n{marker}{line.rstrip()}"
    return res

async def handler(userName,params,msg):
    subject,question=msg_get_data(msg)
    content=msg_apply_reply(await globals()[params['handler']](params,question), question)
    reply_charset='HZ-GB-2312'
    msg_reply = Message()
    msg_reply['From']=userName
    msg_reply['To']=msg['From']
    msg_reply['Subject']=Header("Re: "+subject, reply_charset)
    content=content.replace('\n','\r\n')
    content_gb2312=content.encode('gb2312','replace')
    msg_reply.set_payload(content_gb2312.decode('gb2312'), charset=reply_charset)
    return msg_reply

import logging
logging.basicConfig(filename='askbot.log',filemode='a',level=logging.INFO)
logger=logging.getLogger(__name__)

async def run(userName,params,recvQueue,sendQueue):
    global logger
    while True:
        msgInfo=await recvQueue.get()
        try:
            msg_reply=await handler(userName,params,email.message_from_bytes(msgInfo['msg']))
            msg_reply_data=msg_reply.as_bytes().replace(b'\n',b'\r\n')
            sendQueue.put_nowait({
                'from':userName,
                'to':msgInfo['from'],
                'msg':msg_reply_data
            })
        except:
            logger.error(traceback.format_exc())


