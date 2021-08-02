<?php require('common.php');
$weatherStr='没有天气信息';
$news=apcu_fetch('news_data');
$ncov=apcu_fetch('ncov_data');
try{
  $weather=apcu_fetch('weather_data');
  if($weather){
    $weatherStr=$weather['basic']['city'].'&nbsp;'
      .$weather['now']['cond']['txt'].'&nbsp;'
      .$weather['daily_forecast'][0]['tmp']['min'].'℃/'
      .$weather['daily_forecast'][0]['tmp']['max'].'℃';
    $weatherStr=$weatherStr.'&nbsp;AQI：'.$weather['aqi']['city']['aqi'].'&nbsp;'.$weather['aqi']['city']['qlty'];
  }
}catch(Exception $e){
  error_log('Error while processing weather data at index',$e);
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
        <tr><td colspan='2' height='5px'></td></tr><?php
foreach($news as $item){
?><tr>
  <td width='10px'></td>
  <td><img src='/static/BULLET3.GIF'/> <?=$item['title']?></td>
  </tr><?php
}
?></table></td></tr><tr><td colspan='2' height='28px' align='center'>
  <img src='/static/CONTLINE.GIF'/>
</td></tr><?php
}
if($ncov){
?><tr><td colspan='2'><table width='100%'>
  <tr>
    <td colspan='2' height='24px' valign='middle'>
      <img src='/static/BULL1A.GIF'/>
      <b>抗击疫情</b>　<a href='ncov.php'><font size='2'>查看详情&gt;&gt;</font></a></td>
    <td width='5px' rowspan='100'></td>
  </tr>
  <tr><td colspan='2' height='5px'></td></tr><?php
foreach($ncov['news'] as $item){
?><tr>
  <td width='10px'></td>
  <td><img src='/static/BULLET3.GIF'/> <?=$item['title']?></td>
  </tr><?php
}
?></table></td></tr><tr>
  <tr><td colspan='2' height='5px'></td></tr>
  <td colspan='2'><?php include('ncovtable.php'); ?></td>
</tr><tr><td colspan='2' height='28px' align='center'>
  <img src='/static/CONTLINE.GIF'/>
</td></tr><?php
}
?><tr><td colspan='2' bgcolor='#ffff33' height='8px'></td></tr>
</table></body></html>

