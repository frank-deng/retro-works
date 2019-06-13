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
