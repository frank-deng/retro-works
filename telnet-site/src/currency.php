<?php
if (!defined('IN_SITE')) {
	define('IN_SITE', true);
}
require_once('source/application.php');

$currencies = getCurrencies();
if (!$currencies) {
	$ErrorInfo = lang('Initialization Failed');
	require('source/error.php');
	exit(1);
}

$from = (isset($_GET['from']) && preg_match('/^[A-Za-z]+$/', $_GET['from']) ? strtoupper($_GET['from']) : false);
$to = (isset($_GET['to']) && preg_match('/^[A-Za-z]+$/', $_GET['to']) ? strtoupper($_GET['to']) : false);
$amount = floatval($_GET['amount']);

if ($from && $to) {
	$result = doCurrencyExchange($from, $to, $amount);
	foreach ($currencies as $currency) {
		if ($from == $currency['code']) {
			$nameFromCurrency = $currency['name'];
		}
		if ($to == $currency['code']) {
			$nameToCurrency = $currency['name'];
		}
	}
}

if ($from || $to) {
	setcookie('currencyUsed', $from.'|'.$to, time()+3600*24*365);
} else if (isset($_COOKIE['currencyUsed'])) {
	list($from, $to) = explode('|', $_COOKIE['currencyUsed']);
	$from = preg_match('/^[A-Za-z]+$/', $from) ? strtoupper($from) : false;
	$to = preg_match('/^[A-Za-z]+$/', $to) ? strtoupper($to) : false;
}

?><!DOCTYPE html>
<html>
	<head>
		<meta charset='UTF-8'/>
		<title><?=lang('Currency Exchange')?></title>
	</head>
	<body>
		<table width='100%'><tr>
			<td width='50%'><h1><?=lang('Currency Exchange')?></h1></td>
			<td align='right'><a href='/'>[<?=lang('Back Home Page')?>]</a></td>
		</tr></table>
		<form action='currency.php' method='get'>
			<input type='text' name='amount' size='16' value='<?=$amount?>'/><!--
			--><select name='from'>
				<?php foreach ($currencies as $currency) { ?>
					<option value="<?=$currency['code']?>" <?=$from && $currency['code'] == $from ? 'selected' : ''?>>
						<?=$currency['code'].' '.$currency['name']?>
					</option>
				<?php } ?>
			</select>
			<?=lang('Exchange')?>
			<select name='to'>
				<?php foreach ($currencies as $currency) { ?>
					<option value="<?=$currency['code']?>" <?=$to && $currency['code'] == $to ? 'selected' : ''?>>
						<?=$currency['code'].' '.$currency['name']?>
					</option>
				<?php } ?>
			</select>
			<input type='submit' value='<?=lang('Query')?>'/>
		</form>
		<br/>
		<?php if (isset($result)) { ?>
			<p>
				<?php if ($result !== false) { ?>
					<?=$amount.' '.$nameFromCurrency.' = '.$result.' '.$nameToCurrency?>
				<?php } else { ?>
					<?=lang('Query Failed')?>
				<?php } ?>
			</p>
		<?php } ?>
		<h2><hr/><?=lang('Realtime Exchange Rate')?></h2>
		<table>
			<tr>
				<th align='left'><?=lang('Currency Code')?></th>
				<th align='left'><?=lang('Currency Name')?></th>
				<th align='left'><?=lang('hui_in')?></th>
				<th align='left'><?=lang('chao_in')?></th>
				<th align='left'><?=lang('hui_out')?></th>
				<th align='left'><?=lang('chao_out')?></th>
				<th align='left'><?=lang('zhesuan')?></th>
			</tr>
			<?php foreach ($currencies as $currency) { ?>
				<tr>
					<td><?=$currency['code']?></td>
					<td><?=$currency['name']?></td>
					<td><?=$currency['hui_in']?></td>
					<td><?=$currency['chao_in']?></td>
					<td><?=$currency['hui_out']?></td>
					<td><?=$currency['chao_out']?></td>
					<td><?=$currency['zhesuan']?></td>
				</tr>
			<?php } ?>
		</table>
	</body>
</html>
