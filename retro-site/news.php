<?php require('common.php');
try{
	$loadNews=new FetchNews();
	fetchMultiWait($loadNews);
	$news = $loadNews->fetch();
	if(!is_array($news)){
		$news=[];
	}
	$_TITLE=$_HEADER='今日热点';
}catch(Exception $e){
	die($e->getMessage());
}

require('header.php');
?><table width='100%'>
<?php foreach($news as $idx=>$item){ ?>
<tr><td><img src='/static/BULLET3.GIF'/> <a href='newsDetail.php?key=<?=$item['detail_key']?>'><?=$item['title']?></a></td></tr>
<?php } ?>
<tr><td height='20px' width='100%' align='center' valign='middle'><img src='/static/PROFLINE.GIF'/></td></tr>
</table><?php 
require('footer.php');
