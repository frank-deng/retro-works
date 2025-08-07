import email,asyncio
import email.charset
from email.message import EmailMessage
from traceback import print_exc

CHARSET_ALIAS={
        'cn-gb':'gb2312'
}

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
    
def process_email(msg_raw):
    msg=email.message_from_bytes(msg_raw)
    subject,content=msg_get_data(msg)
    content=msg_apply_reply("测试成功OK。",content)
    reply_charset='hz-gb-2312'
    msg_reply=EmailMessage()
    msg_reply['From']=msg['To']
    msg_reply['To']=msg['From']
    msg_reply['Subject']="Re: "+msg['Subject']
    msg_reply.set_content(content.encode(reply_charset,'ignore'),'text','plain',cte='7bit')
    msg_reply.set_param('charset',reply_charset)
    return msg_reply

async def run(userName,params,recvQueue,sendQueue):
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
