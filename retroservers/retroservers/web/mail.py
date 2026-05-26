import asyncio
import re
import logging
from math import ceil
from aiohttp.web import Request
from aiohttp.web import Response
from aiohttp_jinja2 import template
from aiohttp.web import HTTPFound
from urllib.parse import parse_qs
from retroservers.web import WebServer


@WebServer.get('/mail.asp')
@WebServer.login_required(redirect=True)
@template('mail_frame.html')
async def mail_index(req:Request):
    return {}


@WebServer.get('/mail_left.asp')
@WebServer.login_required()
@template('mail_left.html')
async def mail_left(req:Request):
    return {}


@WebServer.get('/mail_list.asp')
@WebServer.login_required()
@template('mail_list.html')
async def mail_list(req:Request):
    logger=logging.getLogger(__name__)
    folder=req.url.query.get('folder','recv')
    page=1
    try:
        page=int(req.url.query.get('page','1'))
    except (TypeError,ValueError):
        pass
    email_list,total,unread=[],0,0
    if folder=='sent':
        email_list,total=await req.app['MailCenter'].mail_sent(req.uid,page-1)
    else:
        email_list,total,unread=await req.app['MailCenter'].mail_recv(req.uid,page-1)
    total_page=ceil(total/req.app['MailCenter'].pagesize)
    return {
        'email_list':email_list,
        'folder':folder,
        'total':total,
        'total_page':total_page,
        'page':page,
        'unread':unread,
    }


@WebServer.get('/mail_detail.asp')
@WebServer.login_required()
@template('mail_detail.html')
async def mail_detail(req:Request):
    email_id=req.url.query.get('email_id')
    action=req.url.query.get('action')
    email_list=await req.app['MailCenter'].mail_detail(req.uid,email_id)
    await req.app['MailCenter'].mark_read(req.uid,email_id)
    email_top=email_list[0]
    folder=None
    if email_top['from_uid']==req.uid:
        folder='sent'
    return {
        'email_list':email_list,
        'email_id':email_id,
        'allow_reply':req.uid!=email_top['from_uid'],
        'action':action,
        'folder':folder,
    }


@WebServer.get('/mail_editor.asp')
@WebServer.login_required()
@template('mail_editor.html')
async def mail_editor(req:Request):
    logger=logging.getLogger(__name__)
    email_id=req.url.query.get('email_id')
    action=req.url.query.get('action')
    to=''
    cc=''
    subject=''
    email_list=None
    if email_id:
        email_list=await req.app['MailCenter'].mail_detail(req.uid,email_id)
        email_top=email_list[0]
        subject=re.sub(r'^(Re|Fwd):\s*','',email_top['subject'],0,re.IGNORECASE)
        if action=='forward':
            subject='Fwd: '+subject
        elif action=='reply':
            subject='Re: '+subject
            to=await req.app['MailCenter'].get_addr_from_uid(email_top['from_uid'])
    return {
        'email_id':email_id,
        'to':to,
        'cc':cc,
        'subject':subject,
        'body':'',
        'email_list':email_list,
        'action':action,
    }


def __get_recp_list(recp:str):
    recp_list=[s.strip() for s in recp.split(';')]
    return [s for s in list(dict.fromkeys(recp_list)) if s]


@WebServer.post('/mail_editor.asp')
@WebServer.login_required()
@template('mail_editor.html')
async def mail_editor_send(req:Request):
    logger=logging.getLogger(__name__)
    config=req.app['config']
    encoding=config['web'].get('encoding')
    form_data_raw=parse_qs(await req.read())
    form_data={}
    for key_raw in form_data_raw:
        key=key_raw.decode('iso8859-1')
        form_data[key]=form_data_raw[key_raw][0].decode(encoding,errors='replace')
    to_uid,cc_uid={},{}
    subject=form_data.get('subject','').strip()
    body=form_data.get('body','')
    email_id=form_data.get('email_id',None)
    issues=[]
    if not subject:
        issues.append('标题不能为空')
    if form_data.get('action','')=='reply' and not body:
        issues.append('回复邮件正文不能为空')
    to_list=__get_recp_list(form_data.get('to',''))
    cc_list=__get_recp_list(form_data.get('cc',''))
    if (len(to_list)+len(cc_list))==0:
        issues.append('收件人或抄送人必须存在')
    else:
        to_dict=dict.fromkeys(to_list)
        for addr in to_list:
            uid,_=await req.app['MailCenter'].get_uid_from_addr(addr)
            if uid is None:
                issues.append(f'收件人{addr}无效')
            elif uid==req.uid:
                issues.append(f'收件人不能为发件人本人（{addr}）')
            else:
                to_uid[uid]=uid
        for addr in cc_list:
            if addr in to_dict:
                issues.append(f'{addr}不能同时出现在收件人和抄送人中')
                continue
            uid,_=await req.app['MailCenter'].get_uid_from_addr(addr)
            if uid is None:
                issues.append(f'抄送人{addr}无效')
            elif uid==req.uid:
                issues.append(f'抄送人不能为发件人本人（{addr}）')
            else:
                cc_uid[uid]=uid
    if len(issues):
        email_list=None
        if email_id:
            email_list=await req.app['MailCenter'].mail_detail(req.uid,email_id)
        return{
            'email_id':email_id,
            'to':form_data.get('to',''),
            'cc':form_data.get('cc',''),
            'subject':subject,
            'body':body,
            'issues':issues,
            'email_list':email_list,
        }
    await req.app['MailCenter'].send(req.uid,to_uid.keys(),cc_uid.keys(),subject,body,
                           email_id)
    return Response(headers={'Location':'/mail_list.asp?folder=sent'},
                    status=303)


@WebServer.post('/mail_delete.asp')
@WebServer.login_required()
async def mail_delete(req:Request):
    logger=logging.getLogger(__name__)
    form_data_raw=parse_qs(await req.read())
    form_data={}
    for key_raw in form_data_raw:
        key=key_raw.decode('iso8859-1')
        form_data[key]=form_data_raw[key_raw][0].decode('iso8859-1',errors='replace')
    email_id=form_data.get('email_id',None)
    if 'delete_email' in form_data and email_id is not None:
        await req.app['MailCenter'].mail_delete(req.uid,email_id)
    url='/mail_list.asp'
    if 'folder' in form_data:
        url+=f'?folder={form_data['folder']}'
    return Response(headers={'Location':url},status=303)

