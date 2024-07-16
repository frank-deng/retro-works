import email,asyncio
from email.message import EmailMessage
from traceback import print_exc

def process_email(msg_raw):
    msg=email.message_from_bytes(msg_raw)
    content=None
    charset=None
    if msg.is_multipart():
        for part in msg.walk():
            content_type=part.get_content_type()
            content_encoding=part.get_content_transfer_encoding()
            if content_type in {'text/plain','text/html'}:
                charset=part.get_content_charset()
                payload=part.get_payload(decode=True).decode(charset)
    else:
        charset=msg.get_content_charset()
        payload=msg.get_payload(decode=True).decode(charset)
    msg_reply = EmailMessage()
    msg_reply['From']='test@10.0.2.2'
    msg_reply['To']=msg['From']
    msg_reply['Subject']="Re: "+msg['subject']
    msg_reply.set_content(payload.encode(charset),'text','plain',cte='7bit')
    msg_reply.set_param('charset',charset)
    return msg_reply

async def run(params,recvQueue,sendQueue):
    while True:
        msgInfo=await recvQueue.get()
        try:
            print(msgInfo['msg'],'\n')
            msg_reply=process_email(msgInfo['msg'])
            msg_reply_bytes=msg_reply.as_bytes().replace(b'\n',b'\r\n')
            print(msg_reply_bytes,'\n')
            sendQueue.put_nowait({
                'from':'test',
                'to':msgInfo['from'],
                'msg':msg_reply_bytes
            })
        except:
            print_exc()