import aiohttp,asyncio,json,sys
import email
from email.message import EmailMessage
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
                payload=part.get_payload(decode=True).decode(charset)
    else:
        charset=msg.get_content_charset()
        payload=msg.get_payload(decode=True).decode(charset)
    subject=decode(msg['subject'].encode('ascii'), charset)
    return subject,payload,charset
    
def content_append_msg(msg):
    subject,content,charset=msg_get_data(msg)
    marker='> '
    res='\n\n----------'
    if 'Date' in msg:
        res+=f"\n{marker}Date: {msg['Date']}"
    if 'From' in msg:
        res+=f"\n{marker}From: {msg['From']}"
    if 'To' in msg:
        res+=f"\n{marker}To: {msg['To']}"
    if 'Subject' in msg:
        res+=f"\n{marker}Subject: {subject}"
    res+=f"\n{marker}"
    for line in content.rstrip().split('\n'):
        res+=f"\n{marker}{line.rstrip()}"
    return res

async def handler(key,msg):
    subject,question,charset=msg_get_data(msg)
    msg_reply = EmailMessage()
    msg_reply.set_param('charset',charset)
    msg_reply['From']='niwenwoda@10.0.2.2'
    msg_reply['To']=msg['From']
    msg_reply['Subject']="Re: "+msg['Subject']
    access_token=await getAccessToken(key[0],key[1])
    ans=await askBot(access_token,question)
    content=ans+content_append_msg(msg)
    msg_reply.set_content(content.encode(charset,'ignore'),'text','plain',cte='7bit')
    return msg_reply

async def run(params,recvQueue,sendQueue):
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