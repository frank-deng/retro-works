import logging
import os
import functools
from http.cookies import SimpleCookie
import aiohttp_jinja2
import aiohttp_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography.fernet import Fernet
from jinja2 import FileSystemLoader
from markupsafe import Markup, escape
from aiohttp import web
from aiohttp import web_exceptions
from aiohttp.web import HTTPFound
from aiohttp.web import HTTPForbidden
from util import Logger
from util import load_module
import mailcenter


@web.middleware
async def iconv_middleware(request,handler):
    logger=logging.getLogger(__name__)
    try:
        config=request.app['config']
        encoding=config['web'].get('encoding')
        response=await handler(request)
        content_type=response.content_type.lower()
        if content_type=='text/html' and encoding is not None:
            body_str=response.body.decode('utf-8',errors='ignore')
            response.body=body_str.encode(encoding,errors='replace')
            response.headers['content-type']=f"text/html; charset={encoding}"
        return response
    except Exception as e:
        logger.error(e,exc_info=True)


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


class WebServer(Logger):
    MODULES=['web.news', 'web.weather', 'web.index', 'web.mail']
    BASE_DIR='web'
    STATIC_PATH='/static'
    STATIC_DIR='web/static'
    _routes = web.RouteTableDef()

    @staticmethod
    def get(path, **kwargs):
        return WebServer._routes.get(path, **kwargs)

    @staticmethod
    def post(path, **kwargs):
        return WebServer._routes.post(path, **kwargs)

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
        self.__runner=None
        self.__site=None
        self.__host=config['web']['host']
        self.__port=config['web']['port']
        self.__app=web.Application(middlewares=[iconv_middleware])
        self.__app['config']=config
        aiohttp_jinja2.setup(self.__app,
            loader=FileSystemLoader(self.BASE_DIR),
            autoescape=True)
        self.__app.router.add_static(self.STATIC_PATH,self.STATIC_DIR)
        aiohttp_session.setup(self.__app,OldBrowserCookieStorage(Fernet(Fernet.generate_key())))
        self.__app.middlewares.append(session_middleware)
        self.__app.router.add_static(self.STATIC_PATH,self.STATIC_DIR)
        mailcenter.setup(self.__app)
        for item in self.MODULES:
            try:
                load_module(item)
            except Exception as e:
                self.logger.error(f'Failed to load route:{e}',exc_info=True)
        self.__app.add_routes(self._routes)
        env=aiohttp_jinja2.get_env(self.__app)
        env.filters['multiline'] = multiline_filter

    async def __aenter__(self):
        self.__runner=web.AppRunner(self.__app,access_log=None)
        await self.__runner.setup()
        self.__site=web.TCPSite(self.__runner,self.__host,self.__port)
        await self.__site.start()

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        if self.__site is not None:
            await self.__site.stop()
        if self.__runner is not None:
            await self.__runner.cleanup()

