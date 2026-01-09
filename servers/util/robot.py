import asyncio
import aiohttp
from urllib.parse import urlparse,urlunparse
from urllib.robotparser import RobotFileParser
from datetime import datetime, timedelta

from util import Logger

class RobotCheckerSite(Logger):
    def __init__(self,host,timeout_refresh=3600,timeout_failed=120):
        self.__host=host
        self.__timeout_refresh=timeout_refresh
        self.__timeout_failed=timeout_failed
        self.__timeout_fetch=7
        self.__last_load=None
        self.__rp=RobotFileParser()
        self.__load_succ=False
        self.__allow_all=False

    def __check_load_timeout(self):
        now=datetime.now().date()
        if self.__last_load is None:
            self.__last_load=now
            return True
        delta=now-self.__last_load
        tm=int(delta.total_seconds())
        if not self.__load_succ and tm<self.__timeout_failed:
            return False
        elif self.__load_succ and tm<self.__timeout_refresh:
            return False
        else:
            return True

    async def __load(self):
        self.__allow_all=False
        try:
            self.logger.info(f'Load robot.txt for {self.__host}')
            url=f'https://{self.__host}/robots.txt'
            res=None
            async with aiohttp.ClientSession() as session:
                async with session.get(url,timeout=self.__timeout_fetch) as response:
                    if response.status==404:
                        self.__allow_all=True
                        return True
                    response.raise_for_status()
                    res=await response.text()
            if res is None:
                return False
            self.__rp.parse(res.splitlines())
            return True
        except Exception as e:
            self.logger.error(e,exc_info=True)
            return False

    async def can_fetch(self,ua,url):
        if self.__check_load_timeout():
            self.__load_succ=await self.__load()
        if not self.__load_succ:
            return False
        if self.__allow_all:
            return True
        return self.__rp.can_fetch(ua,url)


class RobotChecker(Logger):
    def __init__(self,timeout_refresh=3600,timeout_failed=120):
        self.__timeout_refresh=timeout_refresh
        self.__timeout_failed=timeout_failed
        self.__site={}

    async def can_fetch(self,ua,url):
        parsed=urlparse(url)
        host=urlinfo.netloc
        if host not in self.__site:
            self.__site=RobotCheckerSite(host,self.__timeout_refresh,
                self.__timeout_failed)
        return await self.__site.can_fetch(ua,url)

