<?php require('common.php');
try{
	$loadNews=new FetchNewsDetail(base64_decode($_GET['key']));
	fetchMultiWait($loadNews);
	$data = $loadNews->fetch();
    $title=$data['title'];
    preg_match_all('|<p>((?:(?!</p>).)+)</p>|',$data['content'],$matched);
    $content=[];
    foreach($matched[1] as $line){
        if(preg_match('|^<img.*src=[\'"]([^\'"]+)[\'"].*>$|',$line,$img_match)){
            $url=$img_match[1];
            $line_out=array(
                'type'=>'image',
                'key'=>base64_encode($url)
            );
        }else{
            $line_out=array(
                'type'=>'text',
                'content'=>$line
            );
        }
        array_push($content,$line_out);
    }
	$_TITLE=$_HEADER='今日热点';
}catch(Exception $e){
	die($e->getMessage());
}
require('header.php');
?><h3 align='center'><?=$title?></h3><?php
foreach($content as $line){
    switch($line['type']){
        case 'image':
            ?><p align='center'><img src="image.php?key=<?=$line['key']?>"></p><?php
        break;
        case 'text':
            ?><p>　　<?=$line['content']?></p><?php
        break;
    }
}
?><p align='center'><img src='/static/PROFLINE.GIF'/></p><?php
require('footer.php');
