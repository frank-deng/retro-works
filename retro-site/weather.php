<?php
require('common.php');

$_QUERY=array();
foreach(explode('&',$_SERVER['QUERY_STRING']) as $item){
    $kv=explode('=',$item);
    $key=$kv[0]; $value=$kv[1];
    switch($key){
        case 'location':
            $value=iconv('GB2312','UTF-8',rawurldecode($value));
        break;
    }
    $_QUERY[$key]=$value;
}

$location=null;
if($_QUERY['location']){
	$location=$_QUERY['location'];
	setcookie("location",$location,time()+3600*24*666);
}else if($_COOKIE['location']){
    $location=$_COOKIE['location'];
}
if(!$location){
    header('Location: selectCity.php');
    exit();
}

$loadWeather=null;
if($location){
    $location=explode(';',$location);
    $loadWeather=new FetchWeather($location[0],$location[1]);
    fetchMultiWait($loadWeather);
}

$weather=$loadWeather->fetch();

$_TITLE=$_HEADER='天气预报';
require('header.php');
if(!$weather){
    echo '<h3>没有天气信息</h3>';
    require('footer.php');
    exit();
}
?><p><b>当前城市：</b><?=$loadWeather->getLocationName()?> <font size='2'>[<a href='selectCity.php'>选择城市</a>]</font></p>
<table>
	<tr>
		<th align='left'>天气</th>
		<td rowspan='3' width='10px'></td>
		<td><?=$weather['now']['text']?></td>
		<td rowspan='3' width='20px'></td>
		<th align='left'>温度</th>
		<td rowspan='3' width='10px'></td>
		<td><?=$weather['now']['temp']?>℃</td>
		<td rowspan='2' width='20px'></td>
		<th align='left'>空气污染指数</th>
		<td rowspan='2' width='10px'></td>
		<td><?=$weather['air']['aqi']?></td>
	</tr>
	<tr>
		<th align='left'>湿度</th>
		<td><?=$weather['now']['humidity']?>%</td>
		<th align='left'>能见度</th>
		<td><?=$weather['now']['vis']?>km</td>
		<th align='left'>空气质量等级</th>
		<td><?=$weather['air']['category']?></td>
	</tr>
	<tr>
		<th align='left'>风向</th>
		<td><?=$weather['now']['windDir']?></td>
		<th align='left'>风速</th>
		<td colspan=5><?=$weather['now']['windScale']?>级（<?=$weather['now']['windSpeed']?>km/h）</td>
	</tr>
</table>
<p align='center'><img src='/static/ELEGLINE.GIF'/></p>
<h3>明后天天气预报</h3>
<table width='100%'>
	<tr>
		<th align='left'>日期</th>
		<th align='left'>天气</th>
		<th align='left'>温度</th>
		<th align='left'>湿度</th>
		<th align='left'>风向</th>
		<th align='left'>风速</th>
	</tr>
<?php foreach ($weather['forecast'] as $idx=>$forecast){ if($idx>0){ ?>
	<tr>
		<td><?=$forecast['fxDate']?></td>
		<td><?=$forecast['textDay'].'/'.$forecast['textNight']?></td>
		<td><?=$forecast['tempMin']?>℃/<?=$forecast['tempMax']?>℃</td>
		<td><?=$forecast['humidity']?>%</td>
		<td><?=$forecast['windDirDay']?>/<?=$forecast['windDirNight']?></td>
		<td><?=$forecast['windScaleDay']?>级/<?=$forecast['windScaleNight']?>级</td>
	</tr>
<?php }} ?>
</table>
<p align='center'><img src='/static/ELEGLINE.GIF'/></p>
<h3>气象指数</h3>
<ul>
<?php foreach ($weather['indices'] as $sugg){ ?>
	<li>
		<b><?=$sugg['name']?></b>：<?=$sugg['category']?>
		<div><?=$sugg['text']?></div>
	</li>
<?php } ?>
</ul>
<div align='center'><img src='/static/ELEGLINE.GIF'/><br>&nbsp;</div><?php
require('footer.php');
