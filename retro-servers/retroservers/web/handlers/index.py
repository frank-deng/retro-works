import asyncio
import logging
import os
import json
from aiohttp.web import Request
from aiohttp.web import Response
from aiohttp_jinja2 import template
from datetime import datetime
from aiohttp_session import get_session, new_session
from ..webserver import WebServer
from ..api import WeatherData,NewsAPI

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


def login_ctx(username='',fail_info=None):
    return {
        'title':'登录',
        'header':'用户登录',
        'username':username,
        'fail':fail_info,
        'post_url':'/login.asp'
    }


@WebServer.get('/login.asp')
@template('login.html')
async def login(req:Request):
    return login_ctx('',None)


@WebServer.post('/login.asp')
@template('login.html')
async def do_login(req:Request):
    form_data=await req.post()
    username=form_data.get('username','')
    password=form_data.get('password')
    if not username or not password:
        return login_ctx(username,'用户名和密码不能为空')
    uid=await req.app['MailCenter'].auth(username,password)
    if uid is None:
        return login_ctx(username,'登录失败')
    session=await new_session(req)
    session["uid"]=uid
    return Response(headers={'Location':'/mail.asp'},status=303)


@WebServer.get('/logout.asp')
@WebServer.post('/logout.asp')
async def logout(req:Request):
    session = await get_session(req)
    session.invalidate()
    return Response(headers={'Location':'/'},status=303)

