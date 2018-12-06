#!/usr/bin/env python3
#encoding=UTF-8

import argparse;
parser = argparse.ArgumentParser();
parser.add_argument(
    '--host',
    '-H',
    help='Specify binding host for the server.',
    default=''
);
parser.add_argument(
    '--port',
    '-p',
    help='Specify port for the server.',
    type=int,
    default=8080
);
args = parser.parse_args();

from bottle import route, run, view, template, request, response, redirect;
import models, util, config, urllib;
timerNewsUpdate = None;
timerNewsUpdate2 = None;
timerJokesUpdate = None;

@route('/weather/detail.do')
def weatherDetail():
    city = urllib.parse.unquote(request.cookies.getunicode('city', '')).strip();
    weather = models.getWeatherInfo(city);
    if None != weather:
        return template('weatherDetail', {'weather':weather,});
    else:
        return template('error', {'error':'Failed To Fetch Weather'});

@route('/weather/setcity.do')
@view('weatherSetCity')
def weatherSetCity():
    city = urllib.parse.unquote(request.cookies.getunicode('city', '')).strip();
    return {
        'city': city,
    };

@route('/weather/setcity.do', method='POST')
def doWeatherSetCity():
    response.set_cookie('city', urllib.parse.quote(request.forms.city.strip()), path='/', max_age=3600*24*356);
    response.status = 301;
    response.set_header('Location', '/weather/detail.do');

@route('/news')
def newsList():
    page = int(request.query.get('page', 1));
    data, total = models.getNewsList(page, config.PAGESIZE);
    if (None == data):
        return template('error', {'error':'No News'});
    return template('newsList', {'newsList':data, 'page':page, 'total':total});

@route('/news/<newsId:re:[0-9A-Za-z]+>')
def newsDetail(newsId):
    data = models.getNewsDetail(newsId);
    if (None == data):
        return template('error', {'error':'No News'});
    return template('newsDetail', {'news':data});

@route('/inews')
def iNewsList():
    page = int(request.query.get('page', 1));
    data, total = models.getNewsList(page, config.PAGESIZE, '5572a108b3cdc86cf39001d1');
    if (None == data):
        return template('error', {'error':'No News'});
    return template('iNewsList', {'newsList':data, 'page':page, 'total':total});

@route('/dict')
@view('dict')
def dict():
    word = request.query.word;
    result = models.queryDictionary(word);
    return {
        'word': word,
        'result': result,
    };

@route('/articles')
def articles():
    data = models.getArticles();
    page = int(request.query.get('page', 1));
    if None == data:
        return template('error', {'error':'Failed to load article'});
    return template('articleList', {'articles':data['content'], 'page':page});

@route('/article/<aid:re:[0-9A-Za-z]+>')
def articleDetail(aid):
    title, content = models.getArticleDetail(aid);
    if None == content:
        return template('error', {'error':'Failed to load article'});
    return template('articleDetail', {'title':title, 'article':content});

@route('/jokes')
def showJokes():
    jokes = models.getJokes();
    page = int(request.query.get('page', 1));
    if None == jokes:
        return template('error', {'error':'No Jokes'});
    return template('jokes', {'jokes':jokes, 'page':page});

class UpdateNews:
    def __init__(self, channel=''):
        self.__channel = channel;
    def run(self):
        models.updateNews(self.__channel);

class UpdateJokes:
    def run(self):
        models.updateJokes();

@route('/')
@view('index')
def index():
    global timerNewsUpdate, timerNewsUpdate2, timerJokesUpdate;
    if (None == timerNewsUpdate):
        timerNewsUpdate = util.ThreadInterval(UpdateNews(), config.NEWS_UPDATE_INTERVAL, 'Update News');
        timerNewsUpdate.start();
    if (None == timerNewsUpdate2):
        timerNewsUpdate2 = util.ThreadInterval(UpdateNews('5572a108b3cdc86cf39001d1'), config.NEWS_UPDATE_INTERVAL, 'Update iNews');
        timerNewsUpdate2.start();
    if (None == timerJokesUpdate):
        timerJokesUpdate = util.ThreadInterval(UpdateJokes(), config.JOKES_UPDATE_INTERVAL, 'Update Jokes');
        timerJokesUpdate.start();
    city = urllib.parse.unquote(request.cookies.getunicode('city', '')).strip();
    return {
        'weather':models.getWeatherInfo(city),
        'articles':models.getArticles()['content'][0:17],
    };

try:
    run(server='eventlet', host=args.host, port=args.port);
except KeyboardInterrupt:
    pass;
finally:
    if (None != timerNewsUpdate):
        timerNewsUpdate.stop();
    if (None != timerNewsUpdate2):
        timerNewsUpdate2.stop();
    if (None != timerJokesUpdate):
        timerJokesUpdate.stop();

