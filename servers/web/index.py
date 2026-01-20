import asyncio
import logging
import os
import json
from aiohttp.web import Request
from aiohttp.web import Response
from aiohttp_jinja2 import render_string
from datetime import datetime
from web.weather import WeatherData
from util.fonttool import FontProcessor

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

async def get_news(newsManager):
    logger=logging.getLogger(__name__)
    res=None
    try:
        res=(await newsManager.newsList())[:10]
    except Exception as e:
        logger.error(f'Failed to load news {e}',exc_info=True)
    return res

async def get_blog_data(config):
    logger=logging.getLogger(__name__)
    res=None
    try:
        blog_data_file=config['web'].get('blog_data_file')
        if not blog_data_file or not os.path.isfile(blog_data_file):
            logger.debug(f'Blog data file {blog_data_file} not exist')
            return res
        with open(blog_data_file,'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f'Failed to load blog data {blog_data_file}',exc_info=True)
    return res

async def index(req:Request):
    config=req.app['config']
    links=config['web']['links']
    weather,news,blog=await asyncio.gather(
        get_weather(config,req.cookies.get('location',None)),
        get_news(req.app['newsManager']),
        get_blog_data(config)
    )
    if weather and weather['warning']:
        fontProcesor=FontProcessor('Times New Roman','宋体')
        for item in weather['warning']:
            item['text']=fontProcesor.apply_font(item['text'])

    context={
        'dateStr':datetime.now().strftime('%Y年%m月%d日'),
        'links':links,
        'weather':weather,
        'news':news,
        'blog':blog
    }
    encoding=config['web']['encoding']
    return Response(
        body=render_string("index.html",req,context).encode(encoding,errors='replace'),
        headers={
            'content-type':f"text/html; charset={encoding}"
        }
    )

