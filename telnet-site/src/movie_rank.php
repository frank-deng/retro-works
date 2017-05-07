<?php
if (!defined('IN_SITE')) {
	define('IN_SITE', true);
}
require_once('source/application.php');
$data = getIndexPageData();
echo '<pre>';
var_dump($data);
echo '</pre>';
?><!DOCTYPE html>
<html>
	<head>
		<meta charset='UTF-8'/>
		<title><?=lang('Movie Rank')?></title>
	</head>
	<body>
		<table width='100%'><tr>
			<td width='50%'><h1><?=lang('Movie Rank')?></h1></td>
			<td align='right'><a href='/'>[<?=lang('Back Home Page')?>]</a></td>
		</tr></table>
		<?php if ($data['day']) { ?>
			<hr/>
			<h2><?=lang('Daily Rank')?></h2>
			<table>
				<tr>
					<th align='left'>&nbsp;</th>
					<th align='left'>&nbsp;</th>
					<th align='left'><?=lang('Movie Days')?></th>
					<th align='left'><?=lang('Daily Box Office')?></th>
					<th align='left'><?=lang('Total Box Office')?></th>
				</tr>
				<?php foreach ($data['day'] as $movie) { ?>
					<tr>
						<td><?=$movie['Rank']?></td>
						<td><?=$movie['MovieName']?></td>
						<td><?=$movie['MovieDay']?></td>
						<td><?=$movie['BoxOffice']?><?=lang('万')?></td>
						<td><?=$movie['SumBoxOffice']?><?=lang('万')?></td>
					</tr>
				<?php } ?>
			</table>
		<?php } ?>
		<?php if ($data['weekend']) { ?>
			<hr/>
			<h2><?=lang('Weekend Rank')?></h2>
			<table>
				<tr>
					<th align='left'>&nbsp;</th>
					<th align='left'>&nbsp;</th>
					<th align='left'><?=lang('Movie Days')?></th>
					<th align='left'><?=lang('Weekend Box Office')?></th>
					<th align='left'><?=lang('Total Box Office')?></th>
				</tr>
				<?php foreach ($data['weekend'] as $movie) { ?>
					<tr>
						<td><?=$movie['MovieRank']?></td>
						<td><?=$movie['MovieName']?></td>
						<td><?=$movie['MovieDay']?></td>
						<td><?=$movie['BoxOffice']?><?=lang('万')?></td>
						<td><?=$movie['SumBoxOffice']?><?=lang('万')?></td>
					</tr>
				<?php } ?>
			</table>
		<?php } ?>
		<?php if ($data['week']) { ?>
			<hr/>
			<h2><?=lang('Weekly Rank')?></h2>
			<table>
				<tr>
					<th align='left'>&nbsp;</th>
					<th align='left'>&nbsp;</th>
					<th align='left'><?=lang('Movie Days')?></th>
					<th align='left'><?=lang('Weekly Box Office')?></th>
					<th align='left'><?=lang('Total Box Office')?></th>
				</tr>
				<?php foreach ($data['week'] as $movie) { ?>
					<tr>
						<td><?=$movie['Rank']?></td>
						<td><?=$movie['MovieName']?></td>
						<td><?=$movie['MovieDay']?></td>
						<td><?=$movie['WeekAmount']?><?=lang('万')?></td>
						<td><?=$movie['SumWeekAmount']?><?=lang('万')?></td>
					</tr>
				<?php } ?>
			</table>
		<?php } ?>
	</body>
</html>

