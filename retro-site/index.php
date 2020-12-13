<?php require('config.php');
$weatherStr='没有天气信息';

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

$ch_news=curl_init();
curl_setopt($ch_news, CURLOPT_CONNECTTIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
curl_setopt($ch_news, CURLOPT_TIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
curl_setopt($ch_news, CURLOPT_POST, 1);
curl_setopt($ch_news, CURLOPT_URL, 'http://api.tianapi.com/bulletin/index');
curl_setopt($ch_news, CURLOPT_RETURNTRANSFER, 1);
curl_setopt($ch_news, CURLOPT_POSTFIELDS, http_build_query(array(
  'key'=>$_CONFIG['TIANAPI_KEY']
)));

$task=curl_multi_init();
curl_multi_add_handle($task,$ch_weather);
curl_multi_add_handle($task,$ch_news);

$status=$active=null;
do{
	$status=curl_multi_exec($task,$active);
	if($active){
		curl_multi_select($task);
	}
}while($active && CURLM_OK==$status);

try{
  $news=json_decode(curl_multi_getcontent($ch_news),true)['newslist'];
  $weather=json_decode(curl_multi_getcontent($ch_weather),true)['HeWeather5'][0];
  $weatherStr=$weather['basic']['city'].'&nbsp;'
    .$weather['now']['cond']['txt'].'&nbsp;'
    .$weather['daily_forecast'][0]['tmp']['min'].'℃/'
    .$weather['daily_forecast'][0]['tmp']['max'].'℃';
  try{
    $weatherStr=$weatherStr.'&nbsp;AQI：'.$weather['aqi']['city']['aqi'].'&nbsp;'.$weather['aqi']['city']['qlty'];
  }catch(Exception $e){}
}finally{
  curl_multi_remove_handle($task, $ch_news);
  curl_multi_remove_handle($task, $ch_weather);
  curl_close($ch_news);
  curl_close($ch_weather);
  curl_multi_close($task);
}

$weekStr=array('星期日','星期一','星期二','星期三','星期四','星期五','星期六');
$dateStr=date('Y年n月j日').' '.$weekStr[date('w')];
?><html>
	<head>
		<meta charset='GB2312'/>
    <title>首页 - <?=$dateStr?></title>
	</head>
	<body topmargin='0' leftmargin='0' rightmargin='0' bottommargin='0' bgcolor='#ffffff' background='static/GRAY.JPG'>
    <table width='100%' cellspacing='0'>
      <!--页头和天气模块-->
      <tr>
        <td bgcolor='#ffff33' width='10px' rowspan='100'></td>
        <td bgcolor='#ffff33' bordercolor='#ff0000' rowspan='2' width='50%' height='40px' nowrap>
          <img src='/static/CONTBULL.GIF'/><font size='5' color='#000080'><b>欢迎光临我的信息港</b>&nbsp;</font><img src='static/CONTBULL.GIF'/></td>
          <td bgcolor='#ffff33' bordercolor='#ff0000' nowrap align='right' width='50%'><?=$weatherStr?></td>
        <td bgcolor='#ffff33' width='10px' rowspan='100'></td>
      </tr>
      <tr>
      <td bgcolor='#ffff33' align='right' height='16px'><font size='2'>｜<?php
        foreach($_CONFIG['LINKS'] as $item){ ?><a href='<?=$item["link"]?>'><?=$item['title']?></a>｜<?php
      } ?><a href='weather.php'>天气预报</a>｜</font></td>
      </tr>
      <tr><td colspan='2' height='5px'></td></tr><?php
if($news){
?><tr><td colspan='2'><table width='100%'>
        <tr>
          <td colspan='2' height='24px' valign='middle'>
            <img src='/static/BULL1A.GIF'/>
            <b>今日热点</b>　<a href='news.php'><font size='2'>查看详情&gt;&gt;</font></a></td>
          <td width='5px' rowspan='100'></td>
        </tr>
        <tr><td height='5px'></td></tr><?php
foreach($news as $item){
?><tr>
  <td width='10px'></td>
  <td><img src='/static/BULLET3.GIF'/> <?=$item['title']?></td>
  </tr><?php
}
?></table></td></tr><?php
}
?><tr><td colspan='2' height='28px' align='center'>
    <img src='/static/CONTLINE.GIF'/>
  </td></tr>
  <tr><td colspan='2' bgcolor='#ffff33' height='8px'></td></tr>
</table></body></html>

