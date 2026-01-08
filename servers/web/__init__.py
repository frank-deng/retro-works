import aiohttp_jinja2
import os
import inspect
from jinja2 import FileSystemLoader
from aiohttp import web
from util import Logger
from util import load_module

from web.news import NewsManager

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

class WebServer(Logger):
    __runner=None
    __site=None
    def __init__(self,config):
        self.__host=config['web']['host']
        self.__port=config['web']['port']
        self.__app=web.Application()
        self.__app['config']=config
        self.__app['newsManager']=NewsManager(config['web']['news_api'])
        aiohttp_jinja2.setup(self.__app,
            loader=FileSystemLoader(config['web']['template_dir']),
            autoescape=True)
        for route in config['web']['routes']:
            self.__load_route(route['path'],route)

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

