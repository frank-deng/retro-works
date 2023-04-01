<?php
require('common.php');

$location=null;
try{
    $location=$_COOKIE['location'];
    if($_GET['location']){
        $location=$_GET['location'];
        header('Set-Cookie: location='.urlencode($location).'; expires=Mon, 17-Jan-2038 23:59:59 GMT; path=/');
    }
}catch(Exception $e){
    error_log($e);
}
if(!$location){
    header('Location: selectCity.php');
    exit();
}

$location=explode(',',$location);
$loadWeather=new FetchWeather($location[0],$location[1]);
fetchMultiWait($loadWeather);
$weather=$loadWeather->fetch();
if(!$weather){
    header('Location: selectCity.php');
    exit();
}

$_TITLE='天气预报 - '.$loadWeather->getLocationName();
$_HEADER='天气预报';
$warningColorTable=[
    '蓝色'=>'#0000ff',
    '黄色'=>'#a0a000',
    '橙色'=>'#ff8000',
    '红色'=>'#ff0000',
];
require('header.php');
?><p><b>当前城市：</b><?=$loadWeather->getLocationName()?> <font size='2'>[<a href='selectCity.php'>选择城市</a>]</font></p><?php
if($weather['warning'] && count($weather['warning'])){
?><p>
<?php foreach($weather['warning'] as $item){
?>
<div><font color='<?=$warningColorTable[$item['level']]?>'><?=$item['text']?></font></div>
<?php } ?>
</p><?php
}
?><table>
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
<p align='center'><img src='/static/ELEGLINE.GIF'/></p><?php
require('footer.php');
