<?php
$weekStr=array('星期日','星期一','星期二','星期三','星期四','星期五','星期六');
$dateStr=date('Y年n月j日').' '.$weekStr[date('w')];

error_reporting(0);
mb_internal_encoding('UTF-8');
mb_http_output('GB2312');
mb_language('uni');
mb_regex_encoding('UTF-8');
ob_start('mb_output_handler');
header('content-type: text/html; charset=GB2312');
require('data.php');

