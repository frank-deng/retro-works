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

run(host=args.host, port=args.port);

