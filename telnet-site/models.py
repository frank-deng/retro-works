import json, urllib, httplib2, hashlib;
import config;
from collections import OrderedDict;
import xml.dom.minidom as minidom;

def fetchJSON(url, headers = None, body = None):
    http = httplib2.Http(timeout = config.REQUEST_TIMEOUT);
    if (None != body):
        if isinstance(body, dict):
            if None == headers:
                headers = {'content-type': 'application/x-www-form-urlencoded'};
            else:
                headers['content-type'] = 'application/x-www-form-urlencoded';
            body = urllib.parse.urlencode(body);
        resp,content = http.request(url, 'POST', body, headers=headers);
    else:
        resp,content = http.request(url, 'GET', headers=headers);
    return json.loads(content.decode('UTF-8'));

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
    signParams = OrderedDict(sorted(params.items(), key=lambda x: x[0]));
    sign = '';
    for key in signParams:
        sign += key+str(params[key]);
    sign += config.SHOWAPI_SECRET;
    params['showapi_sign'] = hashlib.md5(sign.encode('UTF-8')).hexdigest();
    try:
        data = fetchJSON(url, body=params);
    except Exception as e:
        print(e);
        return None;
    try:
        del params['showapi_sign'];
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

