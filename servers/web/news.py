import sys
import asyncio
import aiohttp
import logging
from datetime import datetime, timedelta
from functools import cmp_to_key
import re
from urllib.parse import urlparse,urlunparse
import hashlib
import base64
import random

from lxml import html
from aiohttp.web import Request
from aiohttp.web import Response
from aiohttp_jinja2 import render_string
from PIL import Image
from io import BytesIO

from util import Logger
from util.robot import RobotChecker
from util.fonttool import FontProcessor

class NewsManager(Logger):
    __robotChecker=None
    __timeout=5

    @classmethod
    async def can_fetch(self,url):
        if self.__robotChecker is None:
            self.__robotChecker=RobotChecker()
        USER_AGENT = f'Python/{sys.version_info[0]}.{sys.version_info[1]} aiohttp/{aiohttp.__version__}'
        return await self.__robotChecker.can_fetch(USER_AGENT,url)

    @staticmethod
    def __newsListSort(a,b):
        keyA,keyB=a['id'],b['id']
        dateA,dateB=a['date'],b['date']
        if dateA<dateB:
            return 1
        elif dateA>dateB:
            return -1
        elif keyA<keyB:
            return 1
        elif keyA>keyB:
            return 1
        else:
            return 0

    async def __fetch(self,url):
        if not await self.__class__.can_fetch(url):
            raise aiohttp.web.HTTPForbidden()
        async with aiohttp.ClientSession() as session:
            async with session.get(url,timeout=self.__timeout) as response:
                response.raise_for_status()
                return await response.text()

    async def __newsDetailFetchAll(self,url):
        tree=html.fromstring(await self.__fetch(url))
        href_all=None
        for item in tree.xpath('//a'):
            href=item.get('href').strip()
            text=item.text_content().strip()
            if not href or not text or href=='#':
                continue
            if text=='全文':
                href_all=href
        if href_all is None:
            self.logger.debug('No need to load full text')
            return tree
        self.logger.debug('Start load full text')
        await asyncio.sleep(random.uniform(0.8,2.5))
        urlinfo=urlparse(url)
        path=urlinfo.path
        path_new=path.split('/')
        path_new[-1]=href_all
        url_all=urlunparse((
            urlinfo.scheme,
            urlinfo.netloc,
            '/'.join(path_new),
            urlinfo.params,
            urlinfo.query,
            urlinfo.fragment
        ))
        if not await self.__class__.can_fetch(url_all):
            self.logger.debug('Load full text forbidden')
            return tree
        return html.fromstring(await self.__fetch(url_all))

    async def __addImage(self,imgurl):
        digest=hashlib.sha256(imgurl.encode()).digest()
        key=base64.urlsafe_b64encode(digest).decode().rstrip('=')[:12]
        async with self.__imageLinksLock:
            self.__imageLinks[key]=imgurl
        return key

    def __init__(self,host):
        self.__host=host
        self.__newsLinks={}
        self.__newsLinksLock=asyncio.Lock()
        self.__imageLinks={}
        self.__imageLinksLock=asyncio.Lock()

    async def newsList(self):
        res=[]
        resp=await self.__fetch(self.__host)
        href_set=set()
        tree = html.fromstring(resp)
        for item in tree.xpath('//a'):
            href=item.get('href').strip()
            if href in href_set:
                continue
            title=item.text_content().strip()
            if not href or not title or href=='#' or href in href_set:
                continue
            href_set.add(href)
            linkinfo=urlparse(href)
            match=re.search(r'(20(\d{2}[01]\d[0-3]\d))/(\d+)\.html$',linkinfo.path)
            if not match:
                continue
            date_str,key=match[1],match[3]
            date_news=datetime.strptime(date_str,"%Y%m%d").date()
            date_limit=datetime.now().date()-timedelta(days=30)
            if date_news<date_limit:
                continue
            if not await self.__class__.can_fetch(href):
                continue
            res.append({
                'id':key,
                'url':href,
                'date':date_news,
                'title':title
            })
        async with self.__newsLinksLock:
            for item in res:
                self.__newsLinks[item['id']]=item

        return sorted(res,key=cmp_to_key(self.__class__.__newsListSort))

    async def newsDetail(self,newsid):
        newsInfo=None
        async with self.__newsLinksLock:
            newsInfo=self.__newsLinks.get(newsid,None)
        if newsInfo is None:
            return None
        tree=await self.__newsDetailFetchAll(newsInfo['url'])
        content=[]
        for item in tree.xpath('//div[@id="js_article_content" or @id="chan_newsDetail"]//p'):
            imgs=item.xpath('./img')
            for img in imgs:
                src=img.get('src')
                if src and await self.__class__.can_fetch(src):
                    content.append({'type':'image','key':await self.__addImage(src)})
            text=item.text_content().strip()
            if text:
                content.append({'type':'text','content':item.text_content()})
        return {
            'title':newsInfo['title'],
            'date':newsInfo['date'],
            'content':content
        }

    async def newsImage(self,key):
        async with self.__imageLinksLock:
            return self.__imageLinks.get(key,None)

async def news_detail(req:Request):
    config=req.app['config']
    news=await req.app['newsManager'].newsDetail(req.url.query['id'])
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
                'type':'text','content':fontProcesor.apply_font(item['content'])
            })
    context={
        'header':'今日新闻',
        'title':f'{news["title"]} - 今日新闻',
        'news_title':fontProcesor.apply_font(news['title']),
        'news_date':fontProcesor.apply_font(f'{year}年{month}月{day}日'),
        'news_content':news_content
    }
    encoding=config['web']['encoding']
    return Response(
        body=render_string("news.html",req,context).encode(encoding,errors='replace'),
        headers={
            'content-type':f"text/html; charset={encoding}"
        }
    )

async def news_handler(req:Request):
    if 'id' in req.url.query:
        return await news_detail(req)
    config=req.app['config']
    context={
        'header':'今日新闻',
        'title':'今日新闻',
        'news':await req.app['newsManager'].newsList()
    }
    encoding=config['web']['encoding']
    return Response(
        body=render_string("newslist.html",req,context).encode(encoding,errors='replace'),
        headers={
            'content-type':f"text/html; charset={encoding}"
        }
    )

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

async def news_image_handler(req:Request):
    logger=logging.getLogger(__name__)
    config=req.app['config']
    image_url=await req.app['newsManager'].newsImage(req.match_info['image_key'])
    if image_url is None:
        raise aiohttp.web.HTTPNotFound()
    if not await NewsManager.can_fetch(image_url):
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
    return Response(body=image_data)

