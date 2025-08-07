import logging

class Logger:
    _logger=None

    @property
    def logger(self):
        if self._logger is None:
            self._logger=logging.getLogger(self.__class__.__name__)
        return self._logger

