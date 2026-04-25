import asyncio
import aiohttp
from util import Logger


class WeatherData(Logger):
    __timeout=5
    def __init__(self,host,key):
        self.__host=host
        self.__key=key

    async def __fetch(self,session,path,params=None):
        headers={'X-QW-Api-Key':self.__key}
        async with session.get(f'{self.__host}/{path}',params=params,
                               headers=headers,
                               timeout=self.__timeout) as response:
            response.raise_for_status()
            return await response.json()

    async def search_city(self,keyword):
        params={
            'range':'cn',
            'number':20,
            'location':keyword
        }
        res=None
        location_data=[]
        try:
            async with aiohttp.ClientSession() as session:
                location_data=(await self.__fetch(session,'geo/v2/city/lookup',params))['location']
            res=[]
            for item in location_data:
                name=item['adm1']+'-'+item['adm2']
                if item['name']!=item['adm2']:
                    name+='-'+item['name']
                res.append({
                    'id':item['id'],
                    'name':name,
                })
        except Exception as e:
            self.logger.error(f'Failed to search city: {e}',exc_info=True)
            res=None
        return res
    
    async def fetch_weather(self,locid):
        res={}
        async with aiohttp.ClientSession() as session:
            location=(await self.__fetch(session,'geo/v2/city/lookup',{'location':locid}))['location'][0]
            latitude,longitude=location['lat'],location['lon']
            tasks_res=await asyncio.gather(
                self.__fetch(session,'v7/weather/now',{'location':locid}),
                self.__fetch(session,'v7/weather/7d',{'location':locid}),
                self.__fetch(session,f'airquality/v1/current/{latitude}/{longitude}'),
                self.__fetch(session,'v7/warning/now',{'location':locid}),
                self.__fetch(session,'v7/indices/1d',{'location':locid,'type':0})
            )
            res={
                'location':location,
                'now':tasks_res[0]['now'],
                'forecast':tasks_res[1]['daily'][1:],
                'air':tasks_res[2]['indexes'][0],
                'warning':tasks_res[3]['warning'],
                'indices':tasks_res[4]['daily']
            }
        return res

