import asyncio
import logging
import os
import json
from aiohttp.web import Request
from aiohttp.web import Response
from aiohttp_jinja2 import template
from datetime import datetime
from . import WebServer
from .api import WeatherData
from .api import NewsAPI

async def get_weather(config,locid):
    logger=logging.getLogger(__name__)
    if not locid:
        return None
    try:
        warningColorTable={'蓝色':'#0000ff','黄色':'#a0a000',
                           '橙色':'#ff8000','红色':'#ff0000'}
        weatherData=WeatherData(config['web']['weather_api'],
            config['web']['weather_key'])
        weather=await weatherData.fetch_weather(locid)
        location=weather['location']
        location_str=location['adm2']
        if location['name']!=location['adm2']:
            location_str+='-'+location['name']
        weather['location_str']=location_str
        for item in weather['warning']:
            item['level_rgb']=warningColorTable.get(item['level'],'#000000')
        return weather
    except Exception as e:
        logger.error(e,exc_info=True)
        return None

async def get_news(app):
    logger=logging.getLogger(__name__)
    res=None
    try:
        res=(await NewsAPI(app).newsList())[:20]
    except Exception as e:
        logger.error(f'Failed to load news {e}',exc_info=True)
    return res


@WebServer.get('/')
@WebServer.get('/index.asp')
@template('index.html')
async def index(req:Request):
    config=req.app['config']
    links=config['web']['links']
    weather,news=await asyncio.gather(
        get_weather(config,req.cookies.get('location',None)),
        get_news(req.app)
    )
    return {
        'dateStr':datetime.now().strftime('%Y年%m月%d日'),
        'links':links,
        'weather':weather,
        'news':news
    }

