import asyncio
import aiohttp
from urllib.parse import urlparse,urlunparse
from urllib.robotparser import RobotFileParser
from datetime import datetime, timedelta
from . import Logger

class RobotCheckerSite(Logger):
    def __init__(self,host,timeout_refresh=3600,timeout_failed=120):
        self._host=host
        self._timeout_refresh=timeout_refresh
        self._timeout_failed=timeout_failed
        self._timeout_fetch=7
        self._last_load=None
        self._rp=RobotFileParser()
        self._load_succ=False
        self._allow_all=False

    def _check_load_timeout(self):
        now=datetime.now().date()
        if self._last_load is None:
            self._last_load=now
            return True
        delta=now-self._last_load
        tm=int(delta.total_seconds())
        if not self._load_succ and tm<self._timeout_failed:
            return False
        elif self._load_succ and tm<self._timeout_refresh:
            return False
        else:
            return True

    async def _load(self):
        self._allow_all=False
        try:
            self.logger.info(f'Load robot.txt for {self._host}')
            url=f'https://{self._host}/robots.txt'
            res=None
            async with aiohttp.ClientSession() as session:
                async with session.get(url,timeout=self._timeout_fetch) as response:
                    if response.status==404:
                        self._allow_all=True
                        return True
                    response.raise_for_status()
                    res=await response.text()
            if res is None:
                return False
            self._rp.parse(res.splitlines())
            return True
        except Exception as e:
            self.logger.error(e,exc_info=True)
            return False

    async def can_fetch(self,ua,url):
        if self._check_load_timeout():
            self._load_succ=await self._load()
        if not self._load_succ:
            return False
        if self._allow_all:
            return True
        return self._rp.can_fetch(ua,url)


class RobotChecker(Logger):
    def __init__(self,timeout_refresh=3600,timeout_failed=120):
        self._timeout_refresh=timeout_refresh
        self._timeout_failed=timeout_failed
        self._site={}

    async def can_fetch(self,ua,url):
        parsed=urlparse(url)
        urlinfo=urlparse(url)
        host=urlinfo.netloc
        if host not in self._site:
            self._site[host]=RobotCheckerSite(host,self._timeout_refresh,
                self._timeout_failed)
        return await self._site[host].can_fetch(ua,url)

