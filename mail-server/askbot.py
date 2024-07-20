import aiohttp,asyncio,json,sys
import email,email.charset
from email.message import EmailMessage
from email.charset import Charset
from codecs import decode
from traceback import print_exc

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
    url=f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={access_token}"
    jsonData={
        'messages':[
            {
                'role':'user',
                'content':question
            }
        ]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url,json=jsonData) as response:
            res=json.loads(await response.text())
            return res.get('result',None)
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
    charset=Charset(charset).get_output_charset()
    subject,subjectCharset=email.header.decode_header(msg['Subject'])[0]
    if subjectCharset is None:
        subjectCharset=charset
    subjectCharset=Charset(subjectCharset).get_output_charset()
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

async def handler(key,msg):
    subject,question=msg_get_data(msg)
    access_token=await getAccessToken(key[0],key[1])
    content=msg_apply_reply(await askBot(access_token,question), question)
    reply_charset='hz-gb-2312'
    msg_reply = EmailMessage()
    msg_reply['From']='niwenwoda@10.0.2.2'
    msg_reply['To']=msg['From']
    msg_reply['Subject']=f"Re: {subject.encode(reply_charset).decode('ascii')}"
    msg_reply.set_content(content.encode(reply_charset,'ignore'),'text','plain',cte='7bit')
    msg_reply.set_param('charset',reply_charset)
    return msg_reply

async def run(params,recvQueue,sendQueue):
    email.charset.add_codec('cn-gb','gb2312')
    while True:
        msgInfo=await recvQueue.get()
        try:
            msg_reply=await handler(params['erine_key'],email.message_from_bytes(msgInfo['msg']))
            sendQueue.put_nowait({
                'from':'test',
                'to':msgInfo['from'],
                'msg':msg_reply.as_bytes().replace(b'\n',b'\r\n')
            })
        except:
            print_exc()