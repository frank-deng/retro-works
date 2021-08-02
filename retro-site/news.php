<?php require('common.php');
try{
  $news=apcu_fetch('news_data');
  if(!is_array($news)){
    $news=[];
  }
  $_TITLE=$_HEADER='今日热点';
}catch(Exception $e){
  die($e->getMessage());
}

require('header.php');
?><table width='100%'><?php
foreach($news as $idx=>$item){
?><?php
  if($idx){
    ?><tr><td height='20px' width='100%' align='center' valign='middle'><img src='/static/PROFLINE.GIF'/></td></tr><?php
  }
?><tr><td align='center'><b><?=$item['title']?></b></td></tr>
<tr><td height='20px' align='center' valign='top'><font size='1' color='#0000ff'><?=$item['source'].' '.$item['mtime']?></font></td></tr>
<tr><td>　　<?=$item['digest']?></td></tr><?php
}
?></table><?php 
require('footer.php');
