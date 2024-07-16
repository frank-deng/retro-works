import aiohttp,asyncio,json,sys
import email
from email.message import EmailMessage

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

async def handler(key,msg):
    question=None
    charset=None
    if msg.is_multipart():
        for part in msg.walk():
            content_type=part.get_content_type()
            content_encoding=part.get_content_transfer_encoding()
            if content_type in {'text/plain','text/html'}:
                charset=part.get_content_charset()
                question=part.get_payload(decode=True).decode(charset)
    else:
        charset=msg.get_content_charset()
        question=msg.get_payload(decode=True).decode(charset)
    if question is None:
        return
    access_token=await getAccessToken(key[0],key[1])
    ans=await askBot(access_token,question)
    msg2 = EmailMessage()
    msg2['From']='niwenwoda@10.0.2.2'
    msg2['To']=msg['From']
    msg2['Subject']="Re: "+msg['subject']
    msg2.set_content(ans.encode(charset),'text','plain',cte='7bit')
    msg2.set_param('charset',charset)
    return msg2

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