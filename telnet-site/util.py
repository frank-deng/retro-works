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

def __parseKeys(query):
    result = '';
    for key in query:
        if key == pagevar:
            continue;
        elif isinstance(key, str):
            result += "<input type='hidden' name='%s' value='%s'/>"%(key, query['key']);
        elif isinstance(key, list) or isinstance(key, tuple):
            result += __parseKeys(query['key'], pagevar);
    return result;

def pager(baseUrl, pagevar, total, cur):
    url = urllib.parse.urlparse(baseUrl);
    query = urllib.parse.parse_qs(url.query);

    queryNext = urllib.parse.urlencode(queryNext, doseq=True);
    urlNext = urllib.parse.urlunparse(urllib.parse.ParseResult(url.scheme, url.netloc, url.path, url.params, queryNext, url.fragment));

    urlForm = urllib.parse.urlunparse(
        urllib.parse.ParseResult(url.scheme, url.netloc, url.path, url.params, '', url.fragment)
    );
    result = "<form action=\"%s\" method='GET'>"%urlForm;
    if cur > 1:
        query[pagevar] = cur-1;
        urlPrev = urllib.parse.urlunparse(
            urllib.parse.ParseResult(
                url.scheme, url.netloc, url.path, url.params,
                urllib.parse.urlencode(query, doseq=True),
                url.fragment
            )
        );
        result += ("<a href=\"%s\">&lt;"+lang('Prev Page')+"</a>&nbsp;")%(urlPrev);
    if cur < total:
        query[pagevar] = cur+1;
        urlNext = urllib.parse.urlunparse(
            urllib.parse.ParseResult(
                url.scheme, url.netloc, url.path, url.params,
                urllib.parse.urlencode(query, doseq=True),
                url.fragment
            )
        );
        result += ("<a href=\"%s\">"+lang('Next Page')+"&gt;</a>&nbsp;")%(urlNext);
    inputBox = "<input type='text' name='%s' maxlength='%d' size='%d' value='%d'/>"%(pagevar, len(str(total)), len(str(total)), cur);
    result += lang('_jump_page')%(total, inputBox);
    del query[pagevar];
    result += "&nbsp;<input type='submit' value='"+lang('OK')+"'/>"+__parseKeys(query);
    result += '</form>';
    return result;

