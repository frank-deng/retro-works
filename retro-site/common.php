<?php
require('config.php');
function fetch_weather(){
    global $_CONFIG;
    $ch_weather=curl_init();
    curl_setopt($ch_weather, CURLOPT_CONNECTTIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
    curl_setopt($ch_weather, CURLOPT_TIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
    curl_setopt($ch_weather, CURLOPT_POST, 1);
    curl_setopt($ch_weather, CURLOPT_URL, 'https://free-api.heweather.com/v5/weather');
    curl_setopt($ch_weather, CURLOPT_SSL_VERIFYPEER, FALSE);
    curl_setopt($ch_weather, CURLOPT_SSL_VERIFYHOST, FALSE);
    curl_setopt($ch_weather, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch_weather, CURLOPT_POSTFIELDS, http_build_query(array(
        'city'=>$_CONFIG['HEWEATHER_CITY'],
        'key'=>$_CONFIG['HEWEATHER_KEY']
    )));
    return $ch_weather;
}
function tianapi_fetch($url){
    global $_CONFIG;
    $ch=curl_init();
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
    curl_setopt($ch, CURLOPT_TIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query(array(
      'key'=>$_CONFIG['TIANAPI_KEY']
    )));
    return $ch;
}

apcu_add('last_update_time',null);
apcu_add('news_data',null);
apcu_add('ncov_data',null);
apcu_add('weather_data',null);

$timestamp=time();
$timestamp_last=apcu_fetch('last_update_time');

$news=apcu_fetch('news_data');
$ncov=apcu_fetch('ncov_data');
$weather=apcu_fetch('weather_data');
if(!$timestamp_last || ($timestamp-$timestamp_last)>60*3 || !$news || !$ncov ||!$weather || $_GET['clear_cache']){
    try{
        $task=curl_multi_init();
        $ch_weather=fetch_weather();
        $ch_news=tianapi_fetch('http://api.tianapi.com/bulletin/index');
        $ch_ncov=tianapi_fetch('http://api.tianapi.com/txapi/ncov/index');
        curl_multi_add_handle($task,$ch_weather);
        curl_multi_add_handle($task,$ch_news);
        curl_multi_add_handle($task,$ch_ncov);

        $status=$active=null;
        do{
            $status=curl_multi_exec($task,$active);
            if($active){
                curl_multi_select($task);
            }
        }while($active && CURLM_OK==$status);

        $weather=$news=$ncov=null;
        try{
            $weather=json_decode(curl_multi_getcontent($ch_weather),true)['HeWeather5'][0];
            apcu_store('weather_data',$weather);
        }catch(Exception $e){
            error_log('Failed to process weather data',$e);
            $weather=null;
        }
        try{
            $news=json_decode(curl_multi_getcontent($ch_news),true)['newslist'];
            apcu_store('news_data',$news);
        }catch(Exception $e){
            error_log('Failed to process news data',$e);
            $news=null;
        }
        try{
            $ncov=json_decode(curl_multi_getcontent($ch_ncov),true)['newslist'][0];
            apcu_store('ncov_data',$ncov);
        }catch(Exception $e){
            error_log('Failed to process ncov data',$e);
            $ncov=null;
        }
        if($weather && $news && $ncov){
            apcu_store('last_update_time',$timestamp);
        }
    }catch(Exception $e){
        error_log('Error fetching data',$e);
        $ncov=null;
    }finally{
        curl_multi_remove_handle($task, $ch_news);
        curl_multi_remove_handle($task, $ch_weather);
        curl_close($ch_news);
        curl_close($ch_weather);
        curl_multi_close($task);
    }
}

mb_internal_encoding('UTF-8');
mb_http_output('GB2312');
mb_http_input('UTF-8');
mb_language('uni');
mb_regex_encoding('UTF-8');
ob_start('mb_output_handler');
header('content-type: text/html; charset=GB2312');
