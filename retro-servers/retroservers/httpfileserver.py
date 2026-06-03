import asyncio
import os
from aiohttp import web
from aiohttp import web_exceptions
from aiohttp.web import HTTPFound
from aiohttp.web import HTTPForbidden
from .util import Logger


async def _handler(req):
    config=req.app['config']
    rootdir=os.path.abspath(config['rootdir'])
    path=req.match_info['path'].strip().strip('/')
    path=os.path.abspath(os.path.join(rootdir,path))
    if not path.startswith(rootdir):
        raise web.HTTPForbidden()
    if os.path.isfile(path):
        return web.FileResponse(path)
    for index_file in config.get('index',['index.html']):
        index_path=os.path.join(path,index_file)
        if os.path.isfile(index_path):
            return web.FileResponse(index_path)
    raise web.HTTPNotFound()


class HTTPFileServer(Logger):
    def __init__(self,config):
        self._runner=None
        self._site=None
        self._config=config[self.__class__.__name__]
        self._host=self._config.get('host','0.0.0.0')
        self._port=self._config.get('port',80)
        self._app=web.Application()
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

