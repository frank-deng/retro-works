import threading, urllib, httplib2, json;
from langpack import lang;
import config;

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

class Cache:
    __data = {};
    __mutex = threading.Lock();
    def __init__(self):
        pass;

    def get(self, key):
        self.__mutex.acquire();
        val = self.__data.get(key);
        self.__mutex.release();
        return val;

    def set(self, key, val):
        self.__mutex.acquire();
        self.__data[key] = val;
        self.__mutex.release();

def pager(baseUrl, pagevar, total, cur):
    query_prev = query_next = cur;
    result = "<form action=\"%s\" method='GET'>"%baseUrl;
    if cur > 1:
        result += ("<a href=\"%s?%s=%d\">&lt;"+lang('Prev Page')+"</a>&nbsp;")%(baseUrl, pagevar, cur-1);
    if cur < total:
        result += ("<a href=\"%s?%s=%d\">"+lang('Next Page')+"&gt;</a>&nbsp;")%(baseUrl, pagevar, cur+1);
    inputBox = "<input type='text' name='%s' maxlength='%d' size='%d' value='%d'/>"%(pagevar, len(str(total)), len(str(total)), cur);
    result += lang('_jump_page')%(total, inputBox);
    result += "&nbsp;<input type='submit' value='"+lang('OK')+"'/>";
    result += '</form>';
    return result;

