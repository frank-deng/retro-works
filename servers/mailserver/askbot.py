import aiohttp,asyncio,json,sys,re
import email
from email.message import EmailMessage
from email.message import Message
from email.header import Header
from codecs import decode
import traceback,logging

CHARSET_ALIAS={
        'cn-gb':'gb2312'
}

def __parse_content(text):
    cur=''
    remainder=''
    isReply=True
    for line in text.split('\n'):
        line=line.rstrip()
        if re.match(r'^[\-]{8,}$',line):
            isReply=False
        elif isReply:
            cur+=line+'\n'
        else:
            remainder+=re.sub(r'^[\:\|\>]\s?','',line,count=1)+'\n'
    return cur,remainder

def parse_content(remain):
    res=[]
    while True:
        text,remain=__parse_content(remain)
        res.append(text)
        if not remain:
            break
    res.reverse()
    return res

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
    
async def ask_erine(params,content):
    key=params['erine_key']
    access_token=await getAccessToken(key[0],key[1])
    if access_token is None:
        return None
    url=f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions_pro?access_token={access_token}"
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
        'messages':messages,
        'temperature':0.01,
        'top_p':0,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url,json=jsonData) as response:
            res=json.loads(await response.text())
            return res.get('result',None)
    return None

async def ask_deepseek(params,content):
    headers={
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': 'Bearer '+params['deepseek_key']
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
    subject,content=msg_get_data(msg)
    conversation=parse_content(content)
    content=msg_apply_reply(await globals()[params['handler']](params,conversation), content)
    reply_charset='HZ-GB-2312'
    msg_reply = Message()
    msg_reply['From']=userName
    msg_reply['To']=msg['From']
    if re.match(r'Re:\s+', subject):
        msg_reply['Subject']=Header(subject, reply_charset)
    else:
        msg_reply['Subject']=Header("Re: "+subject, reply_charset)
    content=content.replace('\n','\r\n')
    content_gb2312=content.encode('gb2312','replace')
    msg_reply.set_payload(content_gb2312.decode('gb2312'), charset=reply_charset)
    return msg_reply

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
        except Exception as e:
            logger.error(e,exc_info=True)


