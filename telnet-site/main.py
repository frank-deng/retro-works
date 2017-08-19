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
    default=80
);
args = parser.parse_args();

from bottle import route, run, view, template, request, response, redirect;
import models, urllib;

@route('/')
@view('index')
def index():
    city = urllib.parse.unquote(request.cookies.getunicode('city'));
    return {
        'weather':models.getWeatherInfo(city),
    };

@route('/weather/detail.do')
def weatherDetail():
    city = urllib.parse.unquote(request.cookies.getunicode('city', '0'));
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
    city = urllib.parse.unquote(request.cookies.getunicode('city', ''));
    return {
        'city': city,
    };

@route('/weather/setcity.do', method='POST')
def doWeatherSetCity():
    response.set_cookie('city', urllib.parse.quote(request.forms.city), path='/', max_age=3600*24*356);
    response.status = 301;
    response.set_header('Location', '/weather/detail.do');

run(host=args.host, port=args.port);

