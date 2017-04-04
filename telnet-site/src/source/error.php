<?php
if (!defined('IN_SITE')) {
	exit('Access Denied!');
}
?><!DOCTYPE html>
<html>
	<head>
		<meta charset='UTF-8'/>
		<title><?=lang('Error')?></title>
	</head>
	<body>
		<p><?=$ErrorInfo?></p>
		<hr/>
		<p><center><a href='/'>[<?=lang('Back Home Page')?>]</a></center></p>
	</body>
</html>

