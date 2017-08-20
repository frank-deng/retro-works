import json, urllib, httplib2, hashlib, threading, html;
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

def showAPIFetchJSON(url, params = {}):
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
    try:
        if (data and data['showapi_res_code'] == 0 and data['showapi_res_body']['ret_code'] == 0):
            return data['showapi_res_body'];
        else:
            return None;
    except KeyError:
        return None;

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

def getNewsList(page = 1, size = 19, channel = None, keyword = None):
    global cache;
    params = {
        'page':page,
        'needHtml':0,
        'needContent':0,
        'needAllList':1,
        'maxResult':size,
    };
    if (channel):
        params['channelId'] = channel;
    if (isinstance(keyword, str) and len(keyword) > 0):
        params['title'] = urllib.parse.quote(keyword);
    data = showAPIFetchJSON('http://route.showapi.com/109-35', params);
    if not data:
        return None, None;
    try:
        contentlist = data['pagebean']['contentlist'];
        for idx, content in enumerate(contentlist):
            if (not content['title'] or content['title'] == ''):
                for titleCandidate in content['allList']:
                    if isinstance(titleCandidate, str):
                        contentlist[idx]['title'] = re.sub(r'^(\s|　)+', titleCandidate[:25]);
                        break;
            content['html'] = '';
            for line in content['allList']:
                if isinstance(line, str):
                    content['html'] += '<p>'+html.escape(line)+'</p>';
            newsid = hashlib.md5((content['title']+content['source']+content['pubDate']+content['html']).encode('UTF-8')).hexdigest();
            contentlist[idx]['newsid'] = newsid;
            contentlist[idx]['html'] = content['html'];
            del contentlist[idx]['allList'];
            cache.set('news'+newsid, contentlist[idx]);
        return contentlist, data['pagebean']['allPages'];
    except KeyError as e:
        print(e);
        return None, None;

def getNewsDetail(newsid):
    global cache;
    return cache.get('news'+newsid);

def getNewsChannelList(forceUpdate = False):
    global cache;
    data = None;
    if (not forceUpdate):
        data = cache.get('newsChannelList');
        if None != data:
            return data;

    dataRemote = showAPIFetchJSON('http://route.showapi.com/109-34');
    if (None == dataRemote):
        return None;

    data = [('0', lang('Up To Date'))];
    for item in dataRemote['channelList']:
        data.append((item['channelId'], item['name']));
    return data;

def getNewsChannelName(channelId):
    global cache;
    if not channelId:
        channelId = '0';
    data = cache.get('newsChannelList');
    if None == data:
        data = getNewsChannelList(True);
    for item in data:
        if item[0] == channelId:
            return item[1];
    return None;

def getJokes(page = 1, size = 19):
    global cache;
    data = showAPIFetchJSON('http://route.showapi.com/341-1', {'page':page,'maxResult':size});
    if not data:
        return None, None;
    try:
        for idx, content in enumerate(data['contentlist']):
            jokeid = hashlib.md5((content['title']+content['text']+content['ct']).encode('UTF-8')).hexdigest();
            data['contentlist'][idx]['id'] = jokeid;
            cache.set('joke'+jokeid, data['contentlist'][idx]);
        return data['contentlist'],data['allPages'];
    except KeyError:
        return None, None;

def getJokeDetail(jokeid):
    global cache;
    return cache.get('joke'+jokeid);

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

