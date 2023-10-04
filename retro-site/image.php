<?php
require('config.php');
require('data.php');

$loadImage=new FetchImage(base64_decode($_GET['key']));
fetchMultiWait($loadImage);
$data=$loadImage->fetch();
if(!$data){
    exit(0);
}
$image=imagecreatefromstring($data);
$width=imagesx($image);
$height=imagesy($image);
$size=320;
if($width>=$height){
    $image_out=imagescale($image,$size,-1,IMG_BICUBIC);
}else{
    $image_out=imagescale($image,round($size*$width/$height),$size,IMG_BICUBIC);
}

header('content-type: image/jpeg');
imagejpeg($image_out,null,-1);
