<?php
if (!defined('IN_SITE')) {
	define('IN_SITE', true);
}
require_once('source/application.php');

$channel = isset($_GET['channel']) && preg_match('/[0-9A-Fa-f]+/', $_GET['channel']) ? $_GET['channel'] : '';
$page = isset($_GET['page']) ? intval($_GET['page']) : 1;
if ($page < 1) {
	$page = 1;
}
$keyword = isset($_GET['keyword']) ? htmlspecialchars($_GET['keyword']) : false;
$detail = isset($_GET['detail']) && preg_match('/[0-9A-Fa-f]+/', $_GET['detail']) ? $_GET['detail'] : false;

if ('select' === $channel) {
	$channels = newsGetChannels(true);
	if (!$channels) {
		$ErrorInfo = lang('No Channel Info, Please Reload');
		require('source/error.php');
		exit(1);
	}

	define('DISPLAY_ROWS', 5);
?><!DOCTYPE html>
<html>
	<head>
		<meta charset='UTF-8'/>
		<title><?=lang('Select Channel')?></title>
	</head>
	<body>
		<h1><?=lang('Select Channel')?><hr/></h1>
		<table width='100%'>
			<tr>
				<?php $i = 0; foreach ($channels as $channelId => $channelName) { ?>
					<?php $dest_url = ($channelId == 0 ? 'news.php' : 'news.php?channel='.$channelId) ?>
					<td width='<?=100/DISPLAY_ROWS?>%'><a href="<?=$dest_url?>"><?=$channelName?></a></td>
					<?php if ((DISPLAY_ROWS - 1) == ($i % DISPLAY_ROWS)) { ?></tr><tr><?php } ?>
				<?php $i++; } ?>
			</tr>
		</table>
	</body>
</html><?php
	exit(0);
}

$channelName = newsGetChannelName($channel);
$query_arr = Array('page' => $page);
if ($channel) {
	$query_arr['channel'] = $channel;
}
if ($keyword) {
	$query_arr['keyword'] = $keyword;
}
$query_str = http_build_query($query_arr);

if (!$channelName) {
	$ErrorInfo = lang('No News');
	require('source/error.php');
	exit(1);
}
if (false !== $detail) {
	$newsDetail = newsGetDetail($detail);
	if (!$newsDetail) {
		$ErrorInfo = lang('No News');
		require('source/error.php');
		exit(1);
	}
} else {
	$news = newsGetList($channel, $page, $keyword);
	if (!$news) {
		$ErrorInfo = lang('No News');
		require('source/error.php');
		exit(1);
	}
}
?><!DOCTYPE html>
<html>
	<head>
		<meta charset='UTF-8'/>
		<title><?=(false !== $detail) ? $newsDetail['title'].' - '.$channelName : $channelName?></title>
	</head>
	<body>
		<?php if (false !== $detail) { ?>
			<h1><?=$newsDetail['title']?></h1>
			<p><?=$newsDetail['source'].'&nbsp;'.$newsDetail['pubDate']?></p>
			<?=$newsDetail['html']?>
			<p><center><a href='news.php?<?=$query_str?>'>[<?=lang('Back')?>]</a></center></p>
		<?php } else { ?>
			<table width='100%'>
				<tr>
					<td width='40%'><b><?=$channelName?></b>&nbsp;<a href='news.php?channel=select'><?=lang('Select Channel')?>&gt;&gt;</a></td>
					<td align='right'>
						<form href='news.php'>
							<?php if ($channel) { ?>
								<input type='hidden' name='channel' value="<?=htmlspecialchars($channel)?>"/>
							<?php } ?>
							<input type='text' name='keyword' size='20' value="<?=htmlspecialchars($keyword)?>"/><input type='submit' value='<?=lang('Search')?>'/><!--
							--><?=lang('_sep')?><!--
							--><a href='/'>[<?=lang('Back Home Page')?>]</a>
						</form>
					</td>
				</tr>
			</table>
			<ul>
				<?php foreach($news['contentlist'] as $idx=>$content) { ?>
					<li><a href="news.php?<?=$query_str?>&detail=<?=$content['key']?>"><?=$content['title']?></a></li>
				<?php } ?>
			</ul>
			<?=pager("news.php?$query_str", 'page', $news['allPages'], $page)?><br/>
		<?php } ?>
	</body>
</html>
