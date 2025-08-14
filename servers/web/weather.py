import asyncio
import aiohttp
import logging
from urllib.parse import parse_qsl
from aiohttp.web import Request
from aiohttp.web import Response
from aiohttp_jinja2 import render_string
from util import Logger
from pprint import pformat

class WeatherData(Logger):
    __host='https://nd2k5bdhyy.re.qweatherapi.com'
    def __init__(self,key):
        self.__key=key

    async def __fetch(self,session,path,params=None):
        headers={'X-QW-Api-Key':self.__key}
        async with session.get(f'{self.__host}/{path}',params=params,
                               headers=headers) as response:
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


async def select_city(req:Request):
    config=req.app['config']
    encoding=config['web']['encoding']
    city=''
    cityList=None
    for key,value in parse_qsl(req.url.raw_query_string,encoding=encoding):
        if key=='city':
            city=value
    if city:
        weatherData=WeatherData(config['web']['heweather_key'])
        cityList=await weatherData.search_city(city)

    context={
        'header':'天气预报',
        'title':'天气预报',
        'city':city,
        'cityList':cityList
    }
    utf8_content=render_string("select_city.html",req,context)
    return Response(
        body=utf8_content.encode(encoding,errors='replace'),
        headers={
            'content-type':f"text/html; charset={encoding}"
        }
    )


async def weather(req:Request):
    logger=logging.getLogger(__name__)
    config=req.app['config']
    locid=req.url.query.get('location',req.cookies.get('location',None))
    logger.debug(f'locid:{locid}')
    if locid is None:
        return Response(headers={'Location':'select_city.asp'})
    weatherData=WeatherData(config['web']['heweather_key'])
    weather=await weatherData.fetch_weather(locid)
    location=weather['location']
    location_str=location['adm1']+'-'+location['adm2']
    if location['name']!=location['adm2']:
        location_str+='-'+location['name']
    warningColorTable={'蓝色':'#0000ff','黄色':'#a0a000',
                       '橙色':'#ff8000','红色':'#ff0000'}
    for item in weather['warning']:
        item['level_rgb']=warningColorTable.get(item['level'],'#000000')
    context={
        'header':'天气预报',
        'title':f'天气预报：{location_str}',
        'location_str':location_str,
    }
    context.update(weather)
    #logger.debug(pformat(context))
    output_encoding=config['web']['encoding']
    headers={
        'content-type':f"text/html; charset={output_encoding}"
    }
    if 'location' in req.url.query:
        headers['Set-Cookie']=f'location={locid}; expires=Mon, 17-Jan-2038 23:59:59 GMT; path=/'
    return Response(
        body=render_string("weather.html",req,context).encode(output_encoding,errors='replace'),
        headers=headers
    )

