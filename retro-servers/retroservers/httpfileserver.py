import asyncio
import os
import base64
import hashlib
from pathlib import Path
from aiohttp import web
from aiohttp import web_exceptions
from aiohttp.web import HTTPFound
from aiohttp.web import HTTPForbidden
from .util import Logger


def _get_page(req,total,pagesize):
    page=req.url.query.get('page','1')
    try:
        page=int(page)
    except ValueError:
        page=1
    max_pages=math.ceil(total/pagesize)
    if page<1:
        page=1
    elif page>max_pages:
        page=max_pages
    return page


def _listdir(path,path_req,show_hidden=False):
    entries = []
    path_proc=Path(path_req)
    parent=path_proc.parent
    if parent != path_proc:
        entries.append({
            'name':'../',
            'is_dir': True,
            'size': 0,
            'href': str(parent),
        })
    with os.scandir(path) as it:
        for entry in it:
            if entry.name in ('.','..'):
                continue
            if not show_hidden and entry.name.startswith('.'):
                continue
            name=f'{entry.name}/' if entry.is_dir() else entry.name
            entries.append({
                'name': name,
                'is_dir': entry.is_dir(),
                'size': entry.stat().st_size if entry.is_file() else 0,
                'mtime': entry.stat().st_mtime,
                'href': os.path.join(path_req,name),
            })
    entries.sort(key=lambda e: (not e['is_dir'], e['name'].lower()))
    return entries


async def _handler(req):
    config=req.app['config']
    rootdir=os.path.abspath(config['rootdir'])
    path_req=req.match_info['path'].strip().strip('/')
    path=os.path.abspath(os.path.join(rootdir,path_req))
    path_req='/'+path_req
    if not path.startswith(rootdir):
        raise web.HTTPForbidden()
    if os.path.isfile(path):
        return web.FileResponse(path)
    if not os.path.isdir(path):
        raise web.HTTPNotFound()
    for index_file in config.get('index',['index.html']):
        index_path=os.path.join(path,index_file)
        if os.path.isfile(index_path):
            return web.FileResponse(index_path)

    flist=_listdir(path,path_req,config.get('show_hidden',False))
    flist_html=''.join([f'<div><a href="{a['href']}">{a['name']}</a></div>' for a in flist])
    encoding=config.get('encoding','utf-8')
    title=f'Index of {path_req}'
    html=f'''<html>
<head><meta charset='{encoding}'/><title>{title}</title></head>
<body><h1>{title}</h1><hr>{flist_html}</body></html>'''
    return web.Response(
        headers={'content-type':f"text/html; charset={encoding}"},
        body=html.encode(encoding,errors='replace')
    )


async def basic_auth_proc(req:web.Request):
    username_check=req.app['config'].get('username')
    password_hash=req.app['config'].get('password')
    # Disable auth by not setting username and password
    if not username_check or not password_hash:
        return True
    auth_header = req.headers.get('Authorization')
    if not auth_header:
        return False
    try:
        scheme, credentials = auth_header.split(' ', 1)
        if scheme.lower() != 'basic':
            return False
        username, password = base64.b64decode(credentials).decode().split(':', 1)
        if username!=username_check:
            return False
        password_hash_in=hashlib.sha256(password.encode('iso8859-1',errors='ignore')).hexdigest()
        if password_hash_in!=password_hash:
            return False
        req['user'] = username
        return True
    except (ValueError, UnicodeDecodeError):
        return False


@web.middleware
async def basic_auth_middleware(req:web.Request,handler):
    if not await basic_auth_proc(req):
        raise web.HTTPUnauthorized(
            headers={'WWW-Authenticate': 'Basic realm="Authentication required"'},
            text='Authentication required'
        )
    else:
        return await handler(req)


class HTTPFileServer(Logger):
    def __init__(self,config):
        self._runner=None
        self._site=None
        self._config=config[self.__class__.__name__]
        self._host=self._config.get('host','0.0.0.0')
        self._port=self._config.get('port',80)
        self._app=web.Application(middlewares=[basic_auth_middleware])
        self._app['config']=self._config
        self._app.router.add_route('GET','/{path:.*}',_handler)

    async def __aenter__(self):
        self._runner=web.AppRunner(self._app,access_log=None)
        await self._runner.setup()
        self._site=web.TCPSite(self._runner,self._host,self._port)
        await self._site.start()

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        if self._site is not None:
            await self._site.stop()
        if self._runner is not None:
            await self._runner.cleanup()

