import logging
import importlib

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

