import asyncio
import aiohttp
import sys
import re
import random
import base64
import hashlib
from datetime import datetime, timedelta
from functools import cmp_to_key
from urllib.parse import urlparse,urlunparse
from lxml import html
from util import Logger
from util.robot import RobotChecker


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


def NewsAPI(app):
    if 'newsManager' not in app:
        app['newsManager']=NewsManager(app['config']['web']['news_api'])
    return app['newsManager']


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

