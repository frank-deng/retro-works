import asyncio
import aiohttp
import logging
import hashlib
import base64
from aiohttp.web import Request
from aiohttp.web import Response
from aiohttp_jinja2 import render_string
from util import Logger

class NewsManager(Logger):
    __host='https://apis.tianapi.com'
    def __init__(self,key):
        self.__key=key
        self.__newsLinks={}
        self.__newsLinksLock=asyncio.Lock()
        self.__imageLinks={}
        self.__imageLinksLock=asyncio.Lock()

    async def __fetch(self,path,params_in=None):
        params={'key':self.__key}
        if params_in is not None:
            params.update(params_in)
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{self.__host}/{path}',data=params) as response:
                return await response.json()

    async def newsList(self,num=10):
        res=await self.__fetch('generalnews/index',{'num':num})
        res=res['result']['newslist']
        async with self.__newsLinksLock:
            for item in res:
                item['id']=item['id'][:12]
                self.__newsLinks[item['id']]=item['url']
        return res

