<?php require('common.php');
try{
	$loadNews=new FetchNewsDetail(base64_decode($_GET['key']));
	fetchMultiWait($loadNews);
	$data = $loadNews->fetch();
    $title=$data['title'];
    preg_match_all('|<p>((?:(?!</p>).)+)</p>|',$data['content'],$matched);
    $content=[];
    foreach($matched[1] as $line){
        if(strpos($line,'<img')!==false){
            continue;
        }
        array_push($content,$line);
    }
	$_TITLE=$_HEADER='今日热点';
}catch(Exception $e){
	die($e->getMessage());
}
require('header.php');
?><h3 align='center'><?=$title?></h3><?php
foreach($content as $line){
    ?><p>　　<?=$line?></p><?php
}
?><p align='center'><img src='/static/PROFLINE.GIF'/></p><?php
require('footer.php');
