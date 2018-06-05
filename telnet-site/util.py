import threading, urllib, httplib2, json, time, datetime;
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
    url = urllib.parse.urlparse(baseUrl);
    query = urllib.parse.parse_qs(url.query);
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
    result += lang('_jump_page')%(cur, total, inputBox);
    if pagevar in query:
        del query[pagevar];
    result += "&nbsp;<input type='submit' value='"+lang('OK')+"'/>";
    for key in query:
        if key == pagevar:
            continue;
        elif isinstance(query[key], str):
            result += "<input type='hidden' name='%s' value='%s'/>"%(key, query[key]);
        elif isinstance(query[key], list) or isinstance(query[key], tuple):
            for item in query[key]:
                result += "<input type='hidden' name='%s' value='%s'/>"%(key, item);
    result += '</form>';
    return result;

class ThreadInterval(threading.Thread):
    def __init__(self, instance, interval, name = None):
        threading.Thread.__init__(self)
        self.__interval = interval;
        self.__instance = instance;
        if (None == name):
            self.__name = instance.__class__.__name__;
        else:
            self.__name = name;

    def __execute(self):
        try:
            self.__instance.run();
            print('{0:%Y-%m-%dT%H:%M:%S}'.format(datetime.datetime.now()) + (' %s executed successfully' % self.__name));
        except Exception as e:
            print('{0:%Y-%m-%dT%H:%M:%S}'.format(datetime.datetime.now()) + (' %s executed with exception:' % self.__name));
            print(str(e));

    def stop(self):
        try:
            stop_method = getattr(self.__instance, "stop", None);
            if callable(stop_method):
                self.__instance.stop();
        finally:
            self.__running = False;

    def run(self):
        self.__running = True;
        self.__timestamp = time.time();
        self.__execute();
        while self.__running:
            time.sleep(0.1);
            timestamp = time.time();
            if ((timestamp - self.__timestamp) > config.NEWS_UPDATE_INTERVAL):
                self.__timestamp = timestamp;
                self.__execute();
        print('{0:%Y-%m-%dT%H:%M:%S}'.format(datetime.datetime.now()) + (' %s stopped' % self.__name));

