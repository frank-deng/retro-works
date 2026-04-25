import logging
import os
import aiohttp_jinja2
import inspect
from jinja2 import FileSystemLoader
from aiohttp import web
from util import Logger
from util import load_module


class StaticWithIndex(Logger):
    def __init__(self,route_param):
        self.__route_param=route_param

    async def __call__(self,req):
        config=req.app['config']
        rootdir=os.path.abspath(self.__route_param['rootdir'])
        path=req.match_info['path'].strip().strip('/')
        path=os.path.abspath(os.path.join(rootdir,path))
        self.logger.debug(f'{rootdir}\n{path}')
        if not path.startswith(rootdir):
            raise web.HTTPForbidden()
        if os.path.isfile(path):
            return web.FileResponse(path)
        for index_file in self.__route_param.get('index',['index.html']):
            index_path=os.path.join(path,index_file)
            if os.path.isfile(index_path):
                return web.FileResponse(index_path)
        raise web.HTTPNotFound()


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


class WebServer(Logger):
    BASE_DIR='web'
    STATIC_PATH='/static'
    STATIC_DIR='web/static'
    _routes = web.RouteTableDef()
    _pre_init=[]
    _links=[]

    @staticmethod
    def get(path, **kwargs):
        return WebServer._routes.get(path, **kwargs)

    @staticmethod
    def post(path, **kwargs):
        return WebServer._routes.post(path, **kwargs)

    @staticmethod
    def pre_init(func):
        WebServer._pre_init.append(func)
        return func

    @staticmethod
    def index_link(label,href):
        WebServer._links.append({'label':label,'href':href})
        def _index_link(func):
            return func
        return _index_link

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
        modules=[
            'web.news',
            'web.weather',
            'web.index',
        ]
        for item in modules:
            load_module(item)
        for _class in self._pre_init:
            _class(self.__app,config)
        self.__app.add_routes(self._routes)
        self.__app['links']=self._links
        #for route in config['web']['routes']:
        #    self.__load_route(route['path'],route)

    def __load_route(self,path,route):
        try:
            if isinstance(path,list):
                for subpath in path:
                    self.__load_route(subpath,route)
                return
            if 'static' in route:
                self.__app.router.add_static(path,route['static'])
                return
            methods=route.get('method','GET')
            module=load_module(route['module'])
            if inspect.isclass(module):
                self.__app.router.add_route(methods,path,module(route))
            else:
                self.__app.router.add_route(methods,path,module)
        except Exception as e:
            self.logger.error(f'Failed to load route:{e}',exc_info=True)

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

