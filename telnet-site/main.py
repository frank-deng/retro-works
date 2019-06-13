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

@route('/')
@view('index')
def index():
    city = urllib.parse.unquote(request.cookies.getunicode('city', '')).strip();
    return {
        'weather':models.getWeatherInfo(city),
        'articles':models.getArticles()['content'][0:18],
    };

try:
    run(server='eventlet', host=args.host, port=args.port);
except KeyboardInterrupt:
    pass;

