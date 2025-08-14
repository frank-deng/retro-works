import asyncio
import aiohttp
import logging
import hashlib
import base64
from lxml import html
from aiohttp.web import Request
from aiohttp.web import Response
from aiohttp_jinja2 import render_string
from util import Logger
from pprint import pformat
from PIL import Image
from io import BytesIO

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

    async def __addImage(self,imgurl):
        digest=hashlib.sha256(imgurl.encode()).digest()
        key=base64.urlsafe_b64encode(digest).decode().rstrip('=')[:12]
        async with self.__imageLinksLock:
            self.__imageLinks[key]=imgurl
        return key

    async def newsList(self):
        res=await self.__fetch('guonei/index',{'num':50})
        res=res['result']['newslist']
        async with self.__newsLinksLock:
            for item in res:
                item['id']=item['id'][:12]
                self.__newsLinks[item['id']]=item['url']
        return res

    async def newsDetail(self,newsid):
        newsLink=None
        async with self.__newsLinksLock:
            newsLink=self.__newsLinks.get(newsid,None)
        if newsLink is None:
            return None
        data=await self.__fetch('htmltext/index',{'url':newsLink})
        tree=html.fromstring(data['result']['content'])
        content=[]
        for item in tree.xpath('//p'):
            imgs=item.xpath('./img')
            for img in imgs:
                src=img.get('src')
                if src:
                    content.append({'type':'image','key':await self.__addImage(src)})
            text=item.text_content().strip()
            if text:
                content.append({'type':'text','content':item.text_content()})
        return {
            'title':data['result']['title'],
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
    context={
        'header':'今日热点',
        'title':'今日热点',
        'news_title':news['title'],
        'news_content':news['content'],
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
        'header':'今日热点',
        'title':'今日热点',
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
    image_data=None
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status==200:
                image_data=await response.read()
            else:
                logger.error(response.text())
    if image_data is None:
        raise aiohttp.web.HTTPNotFound()
    image_max_size=tuple(config['web'].get('image_max_size',[360,960]))
    image_data=await asyncio.to_thread(downscale_image,image_data,image_max_size)
    return Response(body=image_data)

