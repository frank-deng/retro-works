import email,asyncio
import email.charset
from email.message import EmailMessage
from traceback import print_exc
from codecs import decode

def msg_get_data(msg):
    charset=None
    payload=None
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() in {'text/plain','text/html'}:
                charset=part.get_content_charset()
                payload=part.get_payload()
    else:
        charset=msg.get_content_charset()
        payload=msg.get_payload()
    return payload,charset
    
def content_append_msg(msg):
    content,charset=msg_get_data(msg)
    res='\n\n----------'
    for line in content.rstrip().split('\n'):
        res+=(f"\n> {line}").rstrip()
    return res
    
def process_email(msg_raw):
    msg=email.message_from_bytes(msg_raw)
    content,charset=msg_get_data(msg)
    msg_reply = EmailMessage()
    msg_reply.set_param('charset',charset)
    msg_reply['From']=msg['To']
    msg_reply['To']=msg['From']
    msg_reply['Subject']="Re: "+msg['Subject']
    content="测试成功OK。"+content_append_msg(msg)
    msg_reply.set_content(content.encode(charset,'ignore'),'text','plain',cte='7bit')
    return msg_reply

async def run(params,recvQueue,sendQueue):
    email.charset.add_codec('cn-gb','gb2312')
    while True:
        msgInfo=await recvQueue.get()
        try:
            msg_reply=process_email(msgInfo['msg'])
            msg_reply_bytes=msg_reply.as_bytes().replace(b'\n',b'\r\n')
            sendQueue.put_nowait({
                'from':'test',
                'to':msgInfo['from'],
                'msg':msg_reply_bytes
            })
        except:
            print_exc()
            with open('error.eml','wb') as fp:
                fp.write(msgInfo['msg'])
