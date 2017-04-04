<?php
if (!defined('IN_SITE')) {
	define('IN_SITE', true);
}
require_once('source/application.php');

$page = isset($_GET['page']) ? intval($_GET['page']) : 1;
if ($page < 1) {
	$page = 1;
}
$detail = isset($_GET['detail']) && preg_match('/[0-9A-Fa-f]+/', $_GET['detail']) ? $_GET['detail'] : false;

if ($detail !== false) {
	$joke = getJokeDetail($detail);
	if (!$joke) {
		$ErrorInfo = lang('No Jokes');
		require('source/error.php');
		exit(1);
	}
} else {
	$jokes = getJokes($page);
	if (!$jokes) {
		$ErrorInfo = lang('No Jokes');
		require('source/error.php');
		exit(1);
	}
	$allPages = $jokes['allPages'];
	$maxResult = $jokes['maxResult'];
}
?><!DOCTYPE html>
<html>
	<head>
		<meta charset='UTF-8'/>
		<title><?php if ($detail) { echo $joke['title'].' - '; } ?><?=lang('Jokes Collection')?></title>
	</head>
	<body>
		<?php if (false === $detail) { ?>
			<table width='100%'><tr>
				<td width='60%'><h1><?=lang('Jokes Collection')?></h1></td>
				<td align='right'><a href='/'>[<?=lang('Back Home Page')?>]</a></td>
			</tr></table>
			<ul>
				<?php foreach ($jokes['contentlist'] as $i => $content) { ?>
					<li><a href='jokes.php?page=<?=$page?>&detail=<?=$content['id']?>'><?=$content['title']?></a></li>
				<?php } ?>
			</ul>
			<?=pager('jokes.php', 'page', $jokes['allPages'], $page)?><br/>
		<?php } else { ?>
			<h1><?=$joke['title']?></h1>
			<p><?=$joke['text']?></p>
			<p><center>
				<a href='jokes.php?page=<?=$page?>'>[<?=lang('Back')?>]</a>
			</center></p>
		<?php } ?>
	</body>
</html>
