<?php require('common.php');
try{
  $data=apcu_fetch('ncov_data');
  if(!$data){
    die('Failed to load ncov data.');
  }

  $news=$data['news'];
  $highriskarea=$data['riskarea']['high'];
  $midriskarea=$data['riskarea']['mid'];
  $_TITLE=$_HEADER='抗击疫情';
}catch(Exception $e){
  die($e->getMessage());
}

function display_paragraph($text){
    $p_arr=explode("\n",$text);
    $result='';
    foreach($p_arr as $p){
        if($p){
          $result=$result.'<div>　　'.$p.'</div>';
        }
    }
    return $result;
}
require('header.php');
include('ncovtable.php');
?><hr><h3>最新消息</h3><table width='100%'><?php
foreach($news as $idx=>$item){
?><?php
  if($idx){
    ?><tr><td height='10px' width='100%' valign='middle'></td></tr><?php
  }
?><tr><td><b><?=$item['title']?></b></td></tr>
<tr><td height='20px' valign='top'><font size='1' color='#0000ff'><?=$item['infoSource'].' '.$item['pubDateStr']?></font></td></tr>
<tr><td><?=display_paragraph($item['summary'])?></td></tr><?php
}
?></table><?php
?><hr><h3>高风险地区（<?=count($highriskarea,COUNT_NORMAL)?>个）</h3><?php
if($highriskarea){
?><ul><?php foreach($highriskarea as $item){?><li><font color='red'><?=$item?></font></li><?php } ?></ul><?php
}
?><hr><h3>中风险地区（<?=count($midriskarea,COUNT_NORMAL)?>个）</h3><?php
if($midriskarea){
?><ul><?php foreach($midriskarea as $item){?><li><?=$item?></li><?php } ?></ul><?php
} 
require('footer.php');
