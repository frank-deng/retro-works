import asyncio
import time
import os
import platform
import ctypes
import signal   
import functools
from threading import Thread
from util import Logger

class WatchdogHandler(Thread,Logger):
    __running=True
    __flag=False
    __task=None
    __timeout=10
    __feed_interval=0.1
    __check_interval=0.5

    @staticmethod
    def __kill():
        pid=os.getpid()
        if platform.system()=="Windows":
            handle=ctypes.windll.kernel32.OpenProcess(1,0,pid)
            ctypes.windll.kernel32.TerminateProcess(handle,-1)
            ctypes.windll.kernel32.CloseHandle(handle)
        else:
            os.kill(pid,signal.SIGKILL)

    def __init__(self,timeout:int=10):
        super().__init__()
        self.__timeout=timeout

    async def __aenter__(self):
        self.start()
        self.__task=asyncio.create_task(self.__feed_task())
        return self

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        self.__task.cancel()
        await self.__task
        self.__running=False
        self.join()

    async def __feed_task(self):
        try:
            while self.__running:
                self.__flag=True
                await asyncio.sleep(self.__feed_interval)
        except asyncio.CancelledError:
            pass

    def run(self):
        try:
            timestamp_feed=time.time()
            timestamp_inner=time.time()
            while self.__running:
                if self.__flag:
                    timestamp_feed=time.time()
                    self.__flag=False
                elif timestamp_inner-timestamp_feed > self.__timeout:
                    self.logger.critical(f'''Watchdog not fed within {self.__timeout}s. Last fed:{timestamp_feed}, now:{timestamp_inner}''')
                    self.__class__.__kill()
                timestamp_inner=time.time()
                time.sleep(self.__check_interval)
        except Exception as e:
            self.logger.error(e,exc_info=True)


def watchdog(key_timeout:str):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(config,*args,**kwargs):
            async with WatchdogHandler(config.get(key_timeout,10)):
                await func(config,*args,**kwargs)
        return wrapper
    return decorator

