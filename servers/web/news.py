import asyncio
import aiohttp
import logging
import math
from aiohttp.web import Request
from aiohttp.web import Response
from aiohttp_jinja2 import template
from PIL import Image
from io import BytesIO
from util import Logger
from util.fonttool import FontProcessor
from . import WebServer
from .api import NewsAPI


@template("news.html")
async def news_detail(req:Request):
    config=req.app['config']
    news=await NewsAPI(req.app).newsDetail(req.url.query['id'])
    if news is None:
        raise aiohttp.web.HTTPNotFound()
    year,month,day=news['date'].year,news['date'].month,news['date'].day
    fontProcesor=FontProcessor('Times New Roman','宋体')
    news_content=[]
    for item in news['content']:
        if item['type']=='image':
            news_content.append(item)
        else:
            news_content.append({
                'type':'text','content':fontProcesor.apply_font(item['content'],singleLine=True)
            })
    return {
        'header':'今日新闻',
        'title':f'{news["title"]} - 今日新闻',
        'inline_image':config['web'].get('inline_image',False),
        'news_title':fontProcesor.apply_font(news['title'],singleLine=True),
        'news_date':fontProcesor.apply_font(f'{year}年{month}月{day}日',singleLine=True),
        'news_content':news_content
    }


@WebServer.get("/news.asp")
@template('newslist.html')
async def news_handler(req:Request):
    if 'id' in req.url.query:
        return await news_detail(req)
    config=req.app['config']
    page_size=config['web'].get('news_page_size',30)
    news_list=await NewsAPI(req.app).newsList()

    page=req.url.query.get('page','1')
    try:
        page=int(page)
    except ValueError:
        page=1
    max_pages=math.ceil(len(news_list)/page_size)
    if page<1:
        page=1
    elif page>max_pages:
        page=max_pages

    return {
        'header':'今日新闻',
        'title':'今日新闻',
        'news':news_list[page_size*(page-1):page_size*page],
        'page':page,
        'max_pages':max_pages,
    }


def downscale_image(img_data,max_size,quality=80):
    with Image.open(BytesIO(img_data)) as img:
        img_new=img
        width,height=img.width,img.height
        need_resize=False
        if width>max_size[0]:
            height=int(float(height)*float(max_size[0])/float(width))
            width=max_size[0]
            need_resize=True
        if height>max_size[1]:
            width=int(float(width)*float(max_size[1])/float(height))
            height=max_size[1]
            need_resize=True
        if need_resize:
            img_new=img.resize((width,height),Image.LANCZOS)
        outbuf=BytesIO()
        if img_new.mode != 'RGB':
            img_new=img_new.convert('RGB')
        img_new.save(outbuf,format='JPEG',quality=quality)
        return outbuf.getvalue()


@WebServer.get("/news_images/{image_key}.jpg")
async def news_image_handler(req:Request):
    logger=logging.getLogger(__name__)
    config=req.app['config']
    image_url=await NewsAPI(req.app).newsImage(req.match_info['image_key'])
    if image_url is None:
        raise aiohttp.web.HTTPNotFound()
    if not await NewsAPI(req.app).can_fetch(image_url):
        raise aiohttp.web.HTTPForbidden()
    image_data=None
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url,timeout=5) as response:
            if response.status==200:
                image_data=await response.read()
            else:
                logger.error(response.text())
    if image_data is None:
        raise aiohttp.web.HTTPNotFound()
    image_max_size=tuple(config['web'].get('image_max_size',[360,960]))
    image_data=await asyncio.to_thread(downscale_image,image_data,image_max_size)
    return Response(
        body=image_data,
        headers={
            'content-type':"image/jpeg"
        }
    )

