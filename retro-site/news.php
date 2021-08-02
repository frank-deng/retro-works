<?php require('config.php');
try{
  $ch=curl_init();
  curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
  curl_setopt($ch, CURLOPT_TIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
  curl_setopt($ch, CURLOPT_POST, 1);
  curl_setopt($ch, CURLOPT_URL, 'http://api.tianapi.com/bulletin/index');
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
  curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query(array(
    'key'=>$_CONFIG['TIANAPI_KEY']
  )));
  $output = curl_exec($ch);
  curl_close($ch);
  try{
    $news=json_decode($output,true)['newslist'];
    apcu_store('news_data',$news);
  }catch(Exception $e){
    $news=apcu_fetch('news_data');
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
