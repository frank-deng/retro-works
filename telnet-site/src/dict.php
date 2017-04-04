<?php
if (!defined('IN_SITE')) {
	define('IN_SITE', true);
}
require_once('source/application.php');
if (isset($_GET['word'])) {
	$word = htmlspecialchars($_GET['word']);
	$result = queryDictionary($word);
}

?><!DOCTYPE html>
<html>
	<head>
		<meta charset='UTF-8'/>
		<title><?=lang('Dictionary')?></title>
	</head>
	<body>
		<table width='100%'><tr>
			<td width='50%'><h1><?=lang('Dictionary')?></h1></td>
			<td align='right'><a href='/'>[<?=lang('Back Home Page')?>]</a></td>
		</tr></table>
		<form action='dict.php' method='get'>
			<input type='text' name='word' size='30' value="<?=htmlspecialchars($_GET['word'])?>"/><input type='submit' value="<?=lang('Query Dictionary')?>"/>
		</form><br/>
		<?php if (!isset($result)) { ?>
		<?php } else if ($result === false) { ?>
			<p><?=lang('Query Failed')?></p>
		<?php } else if ($result[0]->Trans->Translation == 'Not Found') { ?>
			<p><?=lang('Not Found')?></p>
		<?php } else { ?>
			<p><?=lang('Meaning')?></p>
			<ul><li><?=$result[0]->Trans->Translation?></li></ul>
			<?php if ($result[0]->Sentence) { ?>
				<p><?=lang('Sentence Example')?></p>
				<ol>
					<?php foreach ($result[0]->Sentence as $sentence) { ?>
						<li><p><?=$sentence->Orig?><br/><?=$sentence->Trans?></p></li>
					<?php } ?>
				</ol>
			<?php } ?>
			<?php if ($result[0]->Refer) { ?>
				<p><?=lang('See Also')?></p>
				<ul><li>
					<?php foreach ($result[0]->Refer as $refer) { ?>
						<a href="dict.php?word=<?=htmlspecialchars($refer->Rel)?>"><?=$refer->Rel?></a>&nbsp;
					<?php } ?>
				</li></ul>
			<?php } ?>
		<?php } ?>
		<p><hr/><center><?=lang('_about_dict')?></center></p>
	</body>
</html>

