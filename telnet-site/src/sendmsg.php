<?php
if (!defined('IN_SITE')) {
	define('IN_SITE', true);
}
require_once('source/application.php');

if (!isset($_POST['message'])) {
	http_response_code(400);
	exit('Error');
}
$message = htmlspecialchars(trim($_POST['message']));
$db = new PDO($_G['config']['dbcache']['conn'], $_G['config']['dbcache']['user'], $_G['config']['dbcache']['password']);
$stmt = $db->prepare('INSERT INTO messages_table (text) values (:message)');
$stmt->bindValue('message', $message, PDO::PARAM_STR);
if (!$stmt->execute()) {
	http_response_code(400);
	exit('Error');
}
exit('OK');