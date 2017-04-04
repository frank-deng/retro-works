<?php
if (!defined('IN_SITE')) {
	define('IN_SITE', true);
}
require_once('source/application.php');

define('PAGE_SIZE', 19);

$page = (isset($_GET['page']) ? intval($_GET['page']) : 1);
if ($page < 1) {
	$page = 1;
}

$article_data = false;
if (isset($_GET['id'])) {
	$id = preg_replace('/[^A-Za-z0-9]/', '', $_GET['id']);
	$article_data = getArticleDetail($id);
	if (!$article_data) {
		$ErrorInfo = lang('Failed to load article');
		require('source/error.php');
		exit(1);
	}
} else {
	$data = getArticles();
	$total = count($data);
	$total_pages = intval($total / PAGE_SIZE);
	if ($total % PAGE_SIZE) {
		$total_pages += 1;
	}
	if ($page > $total_pages) {
		$page = $total_pages;
	}
	$data = array_slice($data, ($page - 1) * PAGE_SIZE, PAGE_SIZE);
}
?><!DOCTYPE html>
<html>
	<head>
		<meta charset='UTF-8'/>
		<title><?=isset($_GET['id']) ? $article_data['title'].' - ': ''?><?=lang('My Space')?></title>
	</head>
	<body>
		<?php if (isset($_GET['id'])) { ?>
			<?=$article_data['content']?>
			<p><center><a href='articles.php?page=<?=$page?>'>[<?=lang('Back')?>]</a></center></p>
		<?php } else { ?>
			<table width='100%'><tr>
				<td width='50%'><h1><?=lang('My Space')?></h1></td>
				<td align='right'><a href='/'>[<?=lang('Back Home Page')?>]</a></td>
			</tr></table>
			<ul>
				<?php foreach($data as $article_data) { ?>
					<li><a href='articles.php?page=<?=$page?>&id=<?=htmlspecialchars($article_data['id'])?>'><?=$article_data['title']?></a></li>
				<?php } ?>
			</ul>
			<?=pager('articles.php', 'page', $total_pages, $page)?><br/>
		<?php } ?>
	</body>
</html>
