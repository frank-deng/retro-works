<?php
if (!defined('IN_SITE')) {
	define('IN_SITE', true);
}
require_once('source/application.php');

$dateTime = new DateTime();
$articles = getArticles();

$indexData = getIndexPageData(isset($_COOKIE['city']) ? htmlspecialchars($_COOKIE['city']) : false);
$weatherData = $indexData['weather'];
$news = $indexData['news'];
$movieRank = $indexData['movieRank'];
$jokes = $indexData['jokes'];

?><!DOCTYPE html>
<html>
	<head>
		<meta charset='UTF-8'/>
		<title><?=lang('Index')?></title>
	</head>
	<body>
		<table width='100%'>
			<tr>
				<td width='40%'><?=$dateTime->format(lang('_date_format'))?>&nbsp;<?=$dateTime->format(lang('_time_format'))?>&nbsp;<?=lang('_week_format')[intval($dateTime->format('w'))]?></td>
				<td width='60%' align='right'><?=lang('_sep')?><!--
					--><a href='dict.php'><?=lang('Dictionary')?></a><?=lang('_sep')?><!--
					--><a href='currency.php'><?=lang('Currency Exchange')?></a><?=lang('_sep')?><!--
					--><a href='message.php'><?=lang('Send Message')?></a><?=lang('_sep')?><!--
				--></td>
			</tr>
			<tr><td colspan='2'>
				<?php if ($weatherData) { ?>
					<?=$weatherData['basic']['city']?>&nbsp;<!--
					--><?=$weatherData['now']['cond']['txt']?>&nbsp;<!--
					--><?=$weatherData['daily_forecast'][0]['tmp']['min'].lang('Centidegree')?>/<?=$weatherData['daily_forecast'][0]['tmp']['max'].lang('Centidegree')?>&nbsp;<!--
					--><?php if (isset($weatherData['aqi']['city']['aqi'])) { ?><!--
						--><?=lang('AQI')?><?=$weatherData['aqi']['city']['aqi']?> <?=$weatherData['aqi']['city']['qlty']?><!--
					--><?php } ?>
					<a href='weather.php'><?='['.lang('Weather Detail').']'?></a>
				<?php } else { ?>
					<?=lang('No Weather Information')?>
				<?php } ?>
				<a href='weather.php?action=setcity'><?='['.lang('Change City').']'?></a>
			</td></tr>
			<tr><td colspan='2'>
				<hr/><div><b><?=lang('Up To Date')?></b>&nbsp;<a href='news.php'><?=lang('More')?>&gt;&gt;</a></div>
				<?php if ($news) { ?>
					<ul>
						<?php for($i = 0; $i < 10; $i++) { ?>
							<li><a href='news.php?page=1&detail=<?=$news['contentlist'][$i]['key']?>'><?=$news['contentlist'][$i]['title']?></a></li>
						<?php } ?>
					</ul>
				<?php } else { ?>
					<p><?=lang('No News')?></p>
				<?php } ?>

				<?php if ($movieRank) { ?>
					<hr/><div><b><?=lang('Movie Rank')?></b></div>
					<table width='100%'>
						<tr>
							<th align='left' width='33%'><b><?=lang('Daily Rank')?></b></th>
							<th align='left' width='33%'><b><?=lang('Weekend Rank')?></b></th>
							<th align='left' width='33%'><b><?=lang('Weekly Rank')?></b></th>
						</tr>
						<tr>
							<td valign='top'><ol>
								<?php foreach ($movieRank['daily'] as $item) { ?>
									<li><?=$item['MovieName']?></li>
								<?php } ?>
							</ol></td>
							<td valign='top'><ol>
								<?php foreach ($movieRank['weekend'] as $item) { ?>
									<li><?=$item['MovieName']?></li>
								<?php } ?>
							</ol></td>
							<td valign='top'><ol>
								<?php foreach ($movieRank['weekly'] as $item) { ?>
									<li><?=$item['MovieName']?></li>
								<?php } ?>
							</ol></td>
						</tr>
					</table>
				<?php } ?>
				
				<hr/><div><b><?=lang('Jokes Collection')?></b>&nbsp;<a href='jokes.php'><?=lang('More')?>&gt;&gt;</a></div>
				<table width='100%'><tr>
					<td valign='top' width='50%'>
						<?php if ($jokes) { ?>
							<ul>
								<?php for($i = 0; $i < 5; $i++) { ?>
									<li><a href='jokes.php?page=1&detail=<?=$jokes['contentlist'][$i]['id']?>'><?=$jokes['contentlist'][$i]['title']?></a></li>
								<?php } ?>
							</ul>
						<?php } else { ?>
							<?=lang('No Jokes')?>
						<?php } ?>
					</td>
					<td valign='top' width='50%'>
						<?php if ($jokes) { ?>
							<ul>
								<?php for($i = 5; $i < 10; $i++) { ?>
									<li><a href='jokes.php?page=1&detail=<?=$jokes['contentlist'][$i]['id']?>'><?=$jokes['contentlist'][$i]['title']?></a></li>
								<?php } ?>
							</ul>
						<?php } ?>
					</td>
				</tr></table>

				<hr/><div><b><?=lang('My Space')?></b>&nbsp;<a href='articles.php'><?=lang('More')?>&gt;&gt;</a></div>
				<ul>
					<?php for($i = 0; $i < 10; $i++) { ?>
						<?php if (!isset($articles[$i])) { break; } ?>
						<li><a href='articles.php?id=<?=$articles[$i]['id']?>'><?=$articles[$i]['title']?></a></li>
					<?php } ?>
				</ul>
				
				<hr/><div><?=lang('About');?></div>
			</td></tr>
		</table>
	</body>
</html>

