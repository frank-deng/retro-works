<?php
if (!defined('IN_SITE')) {
	define('IN_SITE', true);
}
require_once('source/application.php');
$status = null;
if (isset($_POST['sendto']) && isset($_POST['message'])) {
	$sendto = trim($_POST['sendto']);
	$message = trim($_POST['message']);
	if (!preg_match('/^[0-9]{1,16}$/', $sendto)) {
		$sendto = '';
	} else if (strlen($message) > 0) {
		$status = sendMessage($sendto, $message);
	}
}
?><!DOCTYPE html>
<html>
	<head>
		<meta charset='UTF-8'/>
		<title><?=lang('Send Message')?></title>
	</head>
	<body>
		<h1><center><?=lang('Send Message')?></center></h1>
		<form action='' method='post'>
			<table>
				<tr>
					<td><?=lang('Message Content')?></td>
					<td><input type='text' name='message' size='60' value="<?=htmlspecialchars($message)?>"/></td>
				</tr>
				<tr>
					<td><?=lang('Send To')?></td>
					<td><input type='text' name='sendto' size='16' maxlength='16' value="<?=$sendto?>"/></td>
				</tr>
				<tr>
					<td>&nbsp;</td>
					<td><input type='submit' value="<?=lang('Send')?>"/></td>
				</tr>
			</table>
		</form>
		<?php if (null !== $status) { ?>
			<p><?=$status ? lang('Message Send Success') : lang('Message Send Failed')?></p>
		<?php } ?>
		<p><hr/><center><a href='/'>[<?=lang('Back Home Page')?>]</a></center></p>
	</body>
</html>

