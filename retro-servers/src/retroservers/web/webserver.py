import logging
import os
import functools
from importlib.resources import files
from datetime import datetime
from http.cookies import SimpleCookie
import aiohttp_jinja2
import aiohttp_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography.fernet import Fernet
from jinja2 import PackageLoader
from markupsafe import Markup, escape
from aiohttp import web
from aiohttp import web_exceptions
from aiohttp.web import HTTPFound
from aiohttp.web import HTTPNotFound
from aiohttp.web import HTTPForbidden
from retroservers.util import Logger,load_module
from retroservers import MailCenter


@web.middleware
async def iconv_middleware(request,handler):
    config=request.app['config']
    encoding=config['web'].get('encoding')
    response=await handler(request)
    content_type=response.content_type.lower()
    if content_type=='text/html' and encoding is not None:
        body_str=response.body.decode('utf-8',errors='ignore')
        response.body=body_str.encode(encoding,errors='replace')
        response.headers['content-type']=f"text/html; charset={encoding}"
    return response


@web.middleware
async def session_middleware(request,handler):
    logger=logging.getLogger(__name__)
    session=await aiohttp_session.get_session(request)
    request.uid=session.get('uid')
    return await handler(request)


class OldBrowserCookieStorage(EncryptedCookieStorage):
    COOKIE_NAME='SESSION_ID'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load_cookie(self, request):
        return request.cookies.get(self.COOKIE_NAME,None)

    def save_cookie(self, response, cookie_data, max_age=None):
        cookie_name=self.COOKIE_NAME
        cookie = SimpleCookie()
        cookie[cookie_name] = cookie_data
        cookie[cookie_name]["path"] = "/"
        cookie[cookie_name]["expires"] = 'Mon, 17-Jan-2038 23:59:59 GMT'
        response.headers.add("Set-Cookie", cookie[cookie_name].OutputString())


def multiline_filter(value):
    if value is None:
        return ""
    escaped_value = escape(str(value))
    result_with_br = escaped_value.replace('\n', Markup('<br>'))
    return Markup(result_with_br)


def to_datetime_filter(timestamp):
    if not timestamp:
        return None
    dt = datetime.fromtimestamp(timestamp)
    hour=dt.hour
    am_pm = "上午" if hour < 12 else "下午"
    hour12 = hour % 12
    if hour12 == 0:
        hour12 = 12
    return f"{dt.year}年{dt.month}月{dt.day}日 {am_pm}{hour12}:{dt.minute}:{dt.second}"


class WebServer(Logger):
    TEMPLATE_DIR='web/template'
    STATIC_PATH='/static'
    STATIC_DIR=files('retroservers')/'web/static'
    _routes = web.RouteTableDef()

    @classmethod
    def get(cls, path, **kwargs):
        return cls._routes.get(path, **kwargs)

    @classmethod
    def post(cls, path, **kwargs):
        return cls._routes.post(path, **kwargs)

    @staticmethod
    def login_required(redirect=False):
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(request):
                if hasattr(request,'uid') and request.uid:
                    return await func(request)
                elif redirect:
                    return HTTPFound(f'/login.asp')
                else:
                    return HTTPForbidden(text="Please login first.")
            return wrapper
        return decorator

    def __init__(self,config):
        self._runner=None
        self._site=None
        self._host=config['web']['host']
        self._port=config['web']['port']
        self._app=web.Application(middlewares=[iconv_middleware])
        self._app['config']=config
        self._app['MailCenter']=MailCenter.get_instance()
        aiohttp_jinja2.setup(self._app,
            loader=PackageLoader('retroservers',self.TEMPLATE_DIR),
            autoescape=True)
        self._app.router.add_static(self.STATIC_PATH,self.STATIC_DIR)
        aiohttp_session.setup(self._app,OldBrowserCookieStorage(Fernet(Fernet.generate_key())))
        self._app.middlewares.append(session_middleware)
        self._app.router.add_static(self.STATIC_PATH,self.STATIC_DIR)
        self._app.add_routes(self._routes)
        env=aiohttp_jinja2.get_env(self._app)
        env.filters['multiline'] = multiline_filter
        env.filters['to_datetime'] = to_datetime_filter

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

