import aiohttp
from util import Logger

class NewsManager(Logger):
    __host='https://apis.tianapi.com'
    def __init__(self,key):
        self.__key=key

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
        return res
