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
import models, urllib;

from multiprocessing.pool import ThreadPool;
@route('/')
@view('index')
def index():
    city = urllib.parse.unquote(request.cookies.getunicode('city', '')).strip();

    pool = ThreadPool(processes=1);
    weatherInfo = pool.apply_async(models.getWeatherInfo, (city,));
    jokes = pool.apply_async(models.getJokes, (1,10));
    newsList = pool.apply_async(models.getNewsList, (1,10));
    articles = pool.apply_async(models.getArticles);
    movieRank = pool.apply_async(models.getMovieRank);

    return {
        'weather':weatherInfo.get(),
        'jokes':jokes.get()[0],
        'news':newsList.get()[0],
        'articles':articles.get()['content'][0:10],
        'movieRank':movieRank.get(),
    };

@route('/weather/detail.do')
def weatherDetail():
    city = urllib.parse.unquote(request.cookies.getunicode('city', '')).strip();
    weather = models.getWeatherInfo(city);
    if None != weather:
        return template('weatherDetail', {
            'weather':weather,
        });
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

@route('/currency')
def currency():
    currencies = models.getCurrencies();
    if not currencies:
        return template('error', {'error':'Initialization Failed'});
    return template('currency', {
        'currencies':currencies,
        'hasResult':False,
        'fromCurrency':request.cookies.getunicode('fromCurrency', ''),
        'toCurrency':request.cookies.getunicode('toCurrency', ''),
        'amount':'',
    });

@route('/currency', method='POST')
def currencyExchage():
    fromCurrency = request.forms.get('from');
    toCurrency = request.forms.to;
    amount = request.forms.amount;
    response.set_cookie('fromCurrency', fromCurrency, path='/', max_age=3600*24*356);
    response.set_cookie('toCurrency', toCurrency, path='/', max_age=3600*24*356);

    currencies = models.getCurrencies();
    if not currencies:
        return template('error', {'error':'Initialization Failed'});
    fromCurrencyName, toCurrencyName = fromCurrency, toCurrency;
    for c in currencies:
        if (fromCurrency == c['code']):
            fromCurrencyName = c['name'];
        if (toCurrency == c['code']):
            toCurrencyName = c['name'];

    return template('currency', {
        'currencies':currencies,
        'hasResult':True,
        'fromCurrency':fromCurrency,
        'toCurrency':toCurrency,
        'fromCurrencyName':fromCurrencyName,
        'toCurrencyName':toCurrencyName,
        'amount':amount,
        'result':models.doCurrencyExchange(fromCurrency, toCurrency, amount),
    });

@route('/dict')
@view('dict')
def dict():
    word = request.query.word;
    result = models.queryDictionary(word);
    return {
        'word': word,
        'result': result,
    };

@route('/news')
@route('/news/<channel:re:[0-9A-Za-z]+>')
def news(channel = None):
    page = int(request.query.get('page', 1));
    keyword = request.query.getunicode('keyword', '').strip();
    news,totalPages = models.getNewsList(page, keyword=keyword, channel=channel);
    if None == news:
        return template('error', {'error':'No News'});
    url = '/news';
    if channel:
        url += '/'+channel;
    return template('newsList', {
        'url':url,
        'query':urllib.parse.urlencode(request.query.decode(), encoding='UTF-8'),
        'news':news,
        'channel':channel,
        'channelName':models.getNewsChannelName(channel),
        'keyword':keyword,
        'totalPages':totalPages,
        'page':page,
    });

@route('/news/detail/<newsid:re:[0-9A-Za-z]+>')
def newsDetail(newsid):
    news = models.getNewsDetail(newsid);
    if None == news:
        return template('error', {'error':'No News'});
    return template('newsDetail', {'news':news});

@route('/news/channels')
@view('newsChannelSel')
def newsChannelSel():
    return {'channelsAll':models.getNewsChannelList(True)};

@route('/jokes')
def jokes():
    page = int(request.query.get('page', 1));
    jokes, totalPages = models.getJokes(page);
    if None == jokes:
        return template('error', {'error':'No Jokes'});
    return template('jokes', {'jokes':jokes, 'totalPages':totalPages, 'page':page});

@route('/jokes/<jokeid:re:[0-9A-Za-z]+>')
def jokeDetail(jokeid):
    joke = models.getJokeDetail(jokeid);
    if None == joke:
        return template('error', {'error':'No Jokes'});
    return template('jokeDetail', {'joke':joke});

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

run(host=args.host, port=args.port);

