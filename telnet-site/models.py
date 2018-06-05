import json, urllib, httplib2, hashlib, threading, html, re;
from langpack import lang;
from util import fetchJSON, Cache;
import config;
from collections import OrderedDict;
import xml.dom.minidom as minidom;

cache = Cache();

def getWeatherInfo(city):
    if not city:
        return None;
    try:
        weatherData = fetchJSON('https://free-api.heweather.com/v5/weather', None, {'city':city, 'key':config.HEWEATHER_KEY});
    except Exception as e:
        print(e);
        return None;
    try:
        weatherData = weatherData['HeWeather5'][0];
        if (weatherData['status'] == 'ok'):
            return weatherData;
        else:
            return None;
    except KeyError:
        return None;

def showAPIFetchJSON(url, params = None):
    if None == params:
        params = {};
    params['showapi_appid'] = config.SHOWAPI_APPID;
    sign = '';
    for key in OrderedDict(sorted(params.items(), key=lambda x: x[0])):
        sign += key+str(params[key]);
    sign += config.SHOWAPI_SECRET;
    params['showapi_sign'] = hashlib.md5(sign.encode('UTF-8')).hexdigest();
    try:
        data = fetchJSON(url, body=params);
    except Exception as e:
        print(e);
        return None;
    keys = list(params.keys());
    for key in keys:
        del params[key];
    params = None;
    try:
        if (data and data['showapi_res_code'] == 0):
            return data['showapi_res_body'];
        else:
            return None;
    except KeyError:
        return None;

def updateNews(channel='', page = 1, pageSize = 100):
    global cache;
    postData = {
        'page': int(page),
        'maxResult': pageSize,
        'needAllList': 1,
    }
    if (channel):
        postData['channelId'] = channel;
    origData = showAPIFetchJSON('http://route.showapi.com/109-35', postData);
    newsList = [];
    if (None == origData):
        return False;
    idx = 0;
    for news in origData['pagebean']['contentlist']:
        # Filter news with no text content
        contentList = [];
        if (None == news.get('allList')):
            continue;
        for content in news['allList']:
            if (isinstance(content, str)):
                contentList.append(content.strip().replace('•', '・'));
        if (len(contentList) < 4):
            continue;
        newsData = {
            'id': news['id'],
            'title': news['title'].strip(),
            'date': news['pubDate'],
            'content': contentList,
        };
        newsList.append(newsData);
        cache.set('news'+news['id'], newsData);
        idx += 1;
    cache.set('newsList'+channel, newsList);
    return True;

def getNewsList(page=1, pageSize=19, channel=''):
    global cache;
    newsList = cache.get('newsList'+channel);
    if (None == newsList):
        return None, 0;
    return newsList[(pageSize*(page-1)): (pageSize*page)], len(newsList);

def getNewsDetail(newsId):
    global cache;
    return cache.get('news'+newsId);

def getCurrencies():
    data = showAPIFetchJSON('http://route.showapi.com/105-30');
    if not data:
        return None;
    try:
        return data['list'];
    except KeyError:
        return None;

def doCurrencyExchange(f, t, a):
    data = showAPIFetchJSON('http://route.showapi.com/105-31', {'fromCode':f, 'toCode':t, 'money':a});
    if not data:
        return None;
    try:
        return data['money'];
    except KeyError:
        return None;

def updateJokes():
    global cache;
    data = showAPIFetchJSON('http://route.showapi.com/107-32');
    if (not data or None == data.get('list')):
        return None;
    result = [];
    for item in data['list']:
        lines = [];
        for line in item['content'].split('<br/>'):
            line = line.strip();
            if (len(line)):
                lines.append(line);
        result.append({
            'title': item['title'],
            'content': lines,
        });
    cache.set('jokes', result);
    return result;

def getJokes():
    global cache;
    return cache.get('jokes');

def queryDictionary(word):
    http = httplib2.Http(timeout = config.REQUEST_TIMEOUT);
    word = word.replace('\r', '').replace('\n', '');
    try:
        resp,content = http.request(
            'http://fy.webxml.com.cn/webservices/EnglishChinese.asmx/Translator',
            'POST',
            body='wordKey='+urllib.parse.quote(word.encode('UTF-8')),
            headers={'content-type': 'application/x-www-form-urlencoded'}
        );
        dom = minidom.parseString(content.decode('UTF-8'));
        root = dom.documentElement;
        translation = root.getElementsByTagName('Translation')[0].firstChild.data;
        if ('Not Found' == translation):
            return 'Not Found';
        result = {
            'trans':translation,
            'sentence':[],
            'refer':[],
        }
        for sentence in root.getElementsByTagName('Sentence'):
            result['sentence'].append({
                'orig':sentence.getElementsByTagName('Orig')[0].firstChild.data,
                'trans':sentence.getElementsByTagName('Trans')[0].firstChild.data,
            });
        for refer in root.getElementsByTagName('Refer'):
            result['refer'].append(refer.getElementsByTagName('Rel')[0].firstChild.data);
        return result;
    except Exception as e:
        print(e);
        return None;

from multiprocessing.pool import ThreadPool;
def __getRank(item):
    if None != item.get('Rank'):
        return item['Rank'];
    elif None != item.get('MovieRank'):
        return item['MovieRank'];
def getMovieRank():
    pool = ThreadPool(processes=3);
    tweekly = pool.apply_async(showAPIFetchJSON, ('http://route.showapi.com/578-1',));
    tdaily = pool.apply_async(showAPIFetchJSON, ('http://route.showapi.com/578-2',));
    tweekend = pool.apply_async(showAPIFetchJSON, ('http://route.showapi.com/578-3',));
    weekly, daily, weekend = tweekly.get(), tdaily.get(), tweekend.get();
    if (None == weekly and None == daily and None == weekend):
        return None;
    result = {'weekly':[], 'daily':[], 'weekend':[]};
    if None != weekly:
        sorted(weekly['datalist'], key=__getRank, reverse=True);
        result['weekly'] = weekly['datalist'];
    if None != daily:
        sorted(daily['datalist'], key=__getRank, reverse=True);
        result['daily'] = daily['datalist'];
    if None != weekend:
        sorted(weekend['datalist'], key=__getRank, reverse=True);
        result['weekend'] = weekend['datalist'];
    return result;

import os, markdown;
def __getKey(item):
    return item['file'];
def getArticles():
    global cache;
    data = cache.get('mySpaceArticles');
    if None != data and data['timeStamp'] == os.stat(config.ARTICLES_PATH).st_mtime:
        return data;

    fileList = [];
    for dirname, dirnames, filenames in os.walk(config.ARTICLES_PATH):
        for f in filenames:
            fd = config.ARTICLES_PATH+os.sep+f;
            if os.path.isfile(fd) and re.search(r'\.md', fd):
                fileList.append(fd);

    data = {'timeStamp':os.stat(config.ARTICLES_PATH).st_mtime, 'content':[]};
    for fpath in fileList:
        title = None;
        with open(fpath) as fp:
            try:
                title = re.sub(r'^#+\s*', '', fp.readlines()[0].strip());
            except Exception as e:
                print(e);
        if None == title:
            continue;
        data['content'].append({
            'id':hashlib.md5(fpath.encode('UTF-8')).hexdigest(),
            'title':title,
            'file':fpath,
            'mtime':os.stat(fpath).st_mtime,
        });
    contentSorted = sorted(data['content'], key=__getKey, reverse=True);
    data['content'] = contentSorted;
    cache.set('mySpaceArticles', data);
    return data;

def getArticleDetail(aid):
    articles = getArticles();
    if None == articles:
        return None, None;
    for a in articles['content']:
        if a['id'] == aid:
            content = None;
            with open(a['file']) as fp:
                content = markdown.markdown(fp.read());
            return a['title'], content;
    return None, None;

