import asyncio
import aiohttp
import logging
from urllib.parse import parse_qsl
from aiohttp.web import Request
from aiohttp.web import Response
from aiohttp_jinja2 import template
from aiohttp_jinja2 import render_template
from util import Logger
from util.fonttool import FontProcessor
from pprint import pformat
from .api import WeatherData
from . import WebServer


@WebServer.get("/select_city.asp")
@template("select_city.html")
async def select_city(req:Request):
    config=req.app['config']
    encoding=config['web']['encoding']
    city=''
    cityList=None
    for key,value in parse_qsl(req.url.raw_query_string,encoding=encoding):
        if key=='city':
            city=value
    if city:
        weatherData=WeatherData(config['web']['weather_api'],
            config['web']['weather_key'])
        cityList=await weatherData.search_city(city)

    return {
        'header':'天气预报',
        'title':'天气预报',
        'city':city,
        'cityList':cityList
    }


@WebServer.get("/weather.asp")
@WebServer.index_link('天气预报',"/weather.asp")
async def weather(req:Request):
    logger=logging.getLogger(__name__)
    config=req.app['config']
    locid=req.url.query.get('location',req.cookies.get('location',None))
    logger.debug(f'locid:{locid}')
    if locid is None:
        return Response(headers={'Location':'select_city.asp'},status=302)
    weatherData=WeatherData(config['web']['weather_api'],
        config['web']['weather_key'])
    weather=await weatherData.fetch_weather(locid)
    location=weather['location']
    location_str=location['adm1']+'-'+location['adm2']
    if location['name']!=location['adm2']:
        location_str+='-'+location['name']
    warningColorTable={'蓝色':'#0000ff','黄色':'#a0a000',
                       '橙色':'#ff8000','红色':'#ff0000'}
    fontProcesor=FontProcessor('Times New Roman','宋体')
    for item in weather['warning']:
        item['level_rgb']=warningColorTable.get(item['level'],'#000000')
        item['text']=fontProcesor.apply_font(item['text'])
    context={
        'header':'天气预报',
        'title':f'天气预报：{location_str}',
        'location_str':location_str,
    }
    context.update(weather)
    logger.debug(pformat(context))
    output_encoding=config['web']['encoding']
    resp=render_template("weather.html",req,context)
    resp.headers['Set-Cookie']=f'location={locid}; expires=Mon, 17-Jan-2038 23:59:59 GMT; path=/'
    return resp

