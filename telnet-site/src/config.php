<?php
if (!defined('IN_SITE')) {
	exit('Access Denied!');
}

return array(
	'language' => 'zh-CN',
	'timezone' => 'Asia/Shanghai',
	'showAPI' => array('appid' => $_SERVER['SHOWAPI_APPID'], 'secret' => $_SERVER['SHOWAPI_SECRET']),
	'heweather_key' => $_SERVER['HEWEATHER_KEY'],
	'curlTimeout' => 7,
	'articlePath' => __DIR__.'/articles/',
	'articleCacheTimeout' => 1800,
	'dbcache' => array(
		'conn' => 'mysql:host=127.0.0.1;dbname=telnet_site;charset=UTF8',
		'user' => 'telnetsite',
		'password' => 'telnet-site',
	),
	'messageTarget' => array(
		'127001' => 'http://localhost/sendmsg.php',
		'127002' => 'http://localhost:8080/sendmsg.php',
	),
);
