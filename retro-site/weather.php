<?php
require('common.php');

$location=$_COOKIE['location'];
if($_GET['location']){
		$location=$_GET['location'];
		setcookie("location",$location,time()+3600*24*666);
}else if(!$location){
		header('Location: selectCity.php');
		exit();
}
try{
	$suggestion_text=array(
		'air'=>'空气污染指数：',
		'comf'=>'人体舒适指数：',
		'cw'=>'洗车指数：',
		'drsg'=>'穿衣指数：',
		'flu'=>'感冒指数：',
		'sport'=>'运动指数：',
		'trav'=>'旅行指数：',
		'uv'=>'紫外线指数：'
	);
	$loadWeather=new FetchWeather();
    fetchMultiWait($loadWeather);
	$weather = $loadWeather->fetch();
	if(!$weather){
		die('Failed to load weather data.');
	}
	$_TITLE=$_HEADER='天气预报';
}catch(Exception $e){
	error_log($e);
	die($e->getMessage());
}

require('header.php');
?><a href='selectCity.php'>选择城市</a>
<table>
	<tr>
		<th align='left'>天气</th>
		<td rowspan='3' width='10px'></td>
		<td><?=$weather['now']['cond']['txt']?></td>
		<td rowspan='3' width='20px'></td>
		<th align='left'>温度</th>
		<td rowspan='3' width='10px'></td>
		<td><?=$weather['daily_forecast'][0]['tmp']['min']?>℃/<?=$weather['daily_forecast'][0]['tmp']['max']?>℃</td>
		<td rowspan='3' width='20px'></td>
		<th align='left'>紫外线指数</th>
		<td rowspan='3' width='10px'></td>
		<td><?=$weather['daily_forecast'][0]['uv']?></td>
	</tr>
	<tr>
		<th align='left'>湿度</th>
		<td><?=$weather['daily_forecast'][0]['hum']?>%</td>
		<th align='left'>能见度</th>
		<td><?=$weather['daily_forecast'][0]['vis']?> km</td>
		<th align='left'>空气污染指数</th>
		<td><?=$weather['aqi']['city']['aqi']?></td>
	</tr>
	<tr>
		<th align='left'>风向</th>
		<td><?=$weather['daily_forecast'][0]['wind']['dir']?></td>
		<th align='left'>风速</th>
		<td><?=$weather['daily_forecast'][0]['wind']['sc']?>级</td>
		<th align='left'>空气质量等级</th>
		<td><?=$weather['aqi']['city']['qlty']?></td>
	</tr>
</table>
<div align='center'><img src='/static/ELEGLINE.GIF'/></div>
<h3>明后天天气预报</h3>
<table width='100%'>
	<tr>
		<th align='left'>日期</th>
		<th align='left'>天气</th>
		<th align='left'>温度</th>
		<th align='left'>湿度</th>
		<th align='left'>紫外线指数</th>
		<th align='left'>能见度</th>
		<th align='left'>风向</th>
		<th align='left'>风速</th>
	</tr>
<?php foreach ($weather['daily_forecast'] as $idx=>$forecast){ if($idx>0){ ?>
	<tr>
		<td><?=$forecast['date']?></td>
		<td><?=$forecast['cond']['txt_d'].'/'.$forecast['cond']['txt_n']?></td>
		<td><?=$forecast['tmp']['min']?>℃/<?=$forecast['tmp']['max']?>℃</td>
		<td><?=$forecast['hum']?>%</td>
		<td><?=$forecast['uv']?></td>
		<td><?=$forecast['vis']?> km</td>
		<td><?=$forecast['wind']['dir']?></td>
		<td><?=$forecast['wind']['sc']?>级</td>
	</tr>
<?php }} ?>
</table>
<div align='center'><img src='/static/ELEGLINE.GIF'/></div>
<h3>气象指数</h3>
<ul>
<?php foreach ($weather['suggestion'] as $key=>$sugg){ ?>
	<li>
		<b><?=$suggestion_text[$key]?></b><?=$sugg['brf']?>
		<div><?=$sugg['txt']?></div>
	</li>
<?php } ?>
</ul><?php
require('footer.php');
