import logging
import importlib
import asyncio


class Logger:
    _logger=None

    @property
    def logger(self):
        if self._logger is None:
            self._logger=logging.getLogger(self.__class__.__name__)
        return self._logger


def load_module(path):
    selector=None
    if ':' in path:
        path,selector=path.split(':')
    module=importlib.import_module(path)
    if selector is not None:
        module=getattr(module,selector)
    return module


class ServerGroup(Logger):
    def __init__(self,config,server_instance,key='servers'):
        self._config=config
        self._instances=[server_instance(c) \
            for c in self._config[key]]

    async def __aenter__(self):
        tasks=await asyncio.gather(*[self._instance_aenter(s) \
                for s in self._instances])
        for i in range(len(tasks)-1,-1,-1):
            _,e=tasks[i]
            if e is not None:
                del self._instances[i]
        return self

    async def _instance_aenter(self,instance):
        try:
            res=await instance.__aenter__()
            return res,None
        except Exception as e:
            self.logger.error(e,exc_info=True)
            return None,e

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        await asyncio.gather(
                *[self._instance_aexit(s,exc_type,exc_val,exc_tb) \
                for s in self._instances])

    async def _instance_aexit(self,instance,exc_type,exc_val,exc_tb):
        try:
            await instance.__aexit__(exc_type,exc_val,exc_tb)
        except Exception as e:
            self.logger.error(e,exc_info=True)

