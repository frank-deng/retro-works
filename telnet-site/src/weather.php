<?php
if (!defined('IN_SITE')) {
	define('IN_SITE', true);
}
require_once('source/application.php');
$action = (isset($_GET['action']) && in_array($_GET['action'], array('setcity', 'detail')) ? $_GET['action'] : 'detail');

if ($action == 'setcity' || !isset($_COOKIE['city'])) {
	if (isset($_POST['city'])) {
		setcookie('city', htmlspecialchars($_POST['city']), time()+3600*24*356);
		header('Location: weather.php');
	}
?><!DOCTYPE html>
<html>
	<head>
		<meta charset='UTF-8'/>
		<title><?=lang('Change City')?></title>
	</head>
	<body>
		<h1><?=lang('Change City')?></h1>
		<form action='weather.php?action=setcity' method='post'>
			<input type='text' name='city' value="<?=htmlspecialchars($_COOKIE['city'])?>"/><input type='submit' value="<?=lang('OK')?>"/>
		</form>
		<p><hr/><center><a href='/'>[<?=lang('Back Home Page')?>]</a></center></p>
	</body>
</html>
<?php
	exit(0);
}

$weather = getWeatherInfo($_COOKIE['city']);
if (!$weather) {
	$ErrorInfo = lang('Failed To Fetch Weather');
	require('source/error.php');
	exit(1);
}
?><!DOCTYPE html>
<html>
	<head>
		<meta charset='UTF-8'/>
		<title><?=$weather['basic']['city'].lang('Weather')?></title>
	</head>
	<body>
		<table width='100%'><tr>
			<td width='50%'>
				<b><?=$weather['basic']['city'].lang('Weather')?></b>
				<a href='weather.php?action=setcity'><?='['.lang('Change City').']'?></a>
			</td>
			<td align='right'><a href='/'>[<?=lang('Back Home Page')?>]</a></td>
		</tr></table>
		<table>
			<tr>
				<th align='left'><?=lang('Weather')?></th>
				<th align='left'><?=lang('Temperature')?></th>
				<th align='left'><?=lang('Humidity')?></th>
				<th align='left'><?=lang('UVLevel')?></th>
				<th align='left'><?=lang('Visibility')?></th>
				<th align='left'><?=lang('Wind Direction')?></th>
				<th align='left'><?=lang('Wind Speed')?></th>
				<th align='left'><?=lang('AQI2')?></th>
				<th align='left'><?=lang('AQILevel')?></th>
			</tr>
			<tr>
				<td><?=$weather['now']['cond']['txt']?></td>
				<td><?=$weather['daily_forecast'][0]['tmp']['min'].lang('Centidegree')?>/<?=$weather['daily_forecast'][0]['tmp']['max'].lang('Centidegree')?></td>
				<td><?=$weather['daily_forecast'][0]['hum'].'%'?></td>
				<td><?=$weather['daily_forecast'][0]['uv']?></td>
				<td><?=$weather['daily_forecast'][0]['vis'].' km'?></td>
				<td><?=$weather['daily_forecast'][0]['wind']['dir']?></td>
				<?php $sc = $weather['daily_forecast'][0]['wind']['sc']; ?>
				<td><?=$sc?><?=preg_match('[\d]', $sc) ? '级' : ''?></td>
				<?php if (isset($weather['aqi']['city']['aqi'])) { ?>
					<td><?=$weather['aqi']['city']['aqi']?></td>
					<td><?=$weather['aqi']['city']['qlty']?></td>
				<?php } ?>
		</table>
		<h2><?=lang('More Forecast', array('days' => count($weather['daily_forecast'])-1))?></h2>
		<table>
			<tr>
				<th align='left'><?=lang('Date')?></th>
				<th align='left'><?=lang('Weather')?></th>
				<th align='left'><?=lang('Temperature')?></th>
				<th align='left'><?=lang('Humidity')?></th>
				<th align='left'><?=lang('UVLevel')?></th>
				<th align='left'><?=lang('Visibility')?></th>
				<th align='left'><?=lang('Wind Direction')?></th>
				<th align='left'><?=lang('Wind Speed')?></th>
			</tr>
			<?php foreach($weather['daily_forecast'] as $i => $forecast) { ?>
				<?php if ($i == 0) { continue; } ?>
				<tr>
					<td><?=$forecast['date']?></td>
					<td><?=$forecast['cond']['txt_d']?>/<?=$forecast['cond']['txt_n']?></td>
					<td><?=$forecast['tmp']['min'].lang('Centidegree')?>/<?=$forecast['tmp']['max'].lang('Centidegree')?></td>
					<td><?=$forecast['hum'].'%'?></td>
					<td><?=$forecast['uv'] >= 0 ? $forecast['uv'] : ''?></td>
					<td><?=$forecast['vis'] >= 0 ? $forecast['vis'].' km' : ''?></td>
					<td><?=$forecast['wind']['dir']?></td>
					<?php $sc = $forecast['wind']['sc']; ?>
					<td><?=$sc?><?=preg_match('[\d]', $sc) ? '级' : ''?></td>
				</tr>
			<?php } ?>
		</table>

		<h2><?=lang('Weather Suggestion')?></h2>
		<ul>
			<?php foreach($weather['suggestion'] as $key => $sugg) { ?>
				<li><p><b><?=lang('_suggestion')[$key]?></b> <?=$sugg['brf']?><br/><?=$sugg['txt']?></p></li>
			<?php } ?>
		</ul>
	</body>
</html>

