<?php
mb_internal_encoding('UTF-8');
mb_http_output('GB2312');
mb_http_input('UTF-8');
mb_language('uni');
mb_regex_encoding('UTF-8');
ob_start('mb_output_handler');
header('content-type: text/html; charset=GB2312');
$_CONFIG=array(
  'HEWEATHER_CITY'=>"南京",
  'HEWEATHER_KEY'=>"ba1326589c0f458690c86e27f52b6a74",
  'TIANAPI_KEY'=>"f1cdbc5696f7bb76280621f98e388c21",
  'REQUEST_TIMEOUT'=>7,
  'LINKS'=>array(
    array(
        'title'=>'我的博客',
        'link'=>'/blog/'
    )
  )
);
global $_CONFIG;

