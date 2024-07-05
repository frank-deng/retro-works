<?php
require('common.php');
$loadNews=new FetchNews();
$loadBlogs=new FetchBlogs();
$loadWeather=null;
$weatherStr='没有天气信息 <font size=2>[<a href=\'selectCity.php\'>选择城市</a>]</font>&nbsp;';
try{
    $location=null;
    if(isset($_COOKIE['location'])){
        $location=$_COOKIE['location'];
    }
    if($location){
        $location=explode(',',$location);
        $loadWeather=new FetchWeather($location[0],$location[1]);
    }
    fetchMultiWait($loadNews,$loadBlogs,$loadWeather);
}catch(Exception $e){
    error_log($e);
}

$news=$loadNews->fetch();
$blogs=$loadBlogs->fetch();
$weather=null;
try{
    if($loadWeather){
        $weather=$loadWeather->fetch();
    }
    if($weather){
        $weatherStr=$loadWeather->getLocationName(true).'&nbsp;'
            .$weather['now']['text'].'&nbsp;'
            .$weather['now']['temp'].'℃';
        if($weather['air']){
            $weatherStr.='&nbsp;AQI：'.$weather['air']['aqi'].'&nbsp;'.$weather['air']['category'];
        }
    }
}catch(Exception $e){
    error_log('Error while processing weather data',$e);
}
?><html>
	<head>
	    <meta charset='GB2312'/>
        <title>首页 - <?=$dateStr?></title>
	</head>
	<body topmargin='0' leftmargin='0' rightmargin='0' bottommargin='0' background='static/GRAY.JPG'>
<!--Weather warning-->
<?php if($weather && is_array($weather['warning']) && count($weather['warning'])){
$warningColorTable=[
    '蓝色'=>'#0000ff',
    '黄色'=>'#a0a000',
    '橙色'=>'#ff8000',
    '红色'=>'#ff0000',
]; ?>
<?php foreach($weather['warning'] as $item){ ?>
<font color='<?=$warningColorTable[$item['level']]?>'>
    <marquee
        bgcolor='#ffffff'
        scrolldelay=100 scrollamount=8>
        <?=$item['text']?>
    </marquee>
</font>
<?php } ?>
<?php } ?>
<!--页头和天气模块-->
<table width='100%' cellspacing='0' cellpadding='0'>
    <tr>
        <td bgcolor='#ffff33' width='10px' rowspan='2'></td>
        <td bgcolor='#ffff33' bordercolor='#ff0000' rowspan='2' height='40px' nowrap>
            <img src='/static/CONTBULL.GIF'/><font size='5' face='黑体' color='#000080'><b>欢迎光临我的信息港</b>&nbsp;</font><img src='static/CONTBULL.GIF'/></td>
        <td bgcolor='#ffff33' bordercolor='#ff0000' nowrap align='right'><?=$weatherStr?></td>
        <td bgcolor='#ffff33' width='10px' rowspan='2'></td>
    </tr>
    <tr>
        <td bgcolor='#ffff33' align='right' height='16px'>
            <font size='2'>｜<?php foreach($_CONFIG['LINKS'] as $item){ ?><a href='<?=$item["link"]?>'><?=$item['title']?></a>｜<?php } ?></font></td>
    </tr>
    <tr>
        <td rowspan=200></td>
        <td height='8px' colspan=2></td>
        <td rowspan=200></td>
    </tr>
    <tr><td colspan=2>
<!--News Module-->
<?php if($news){ ?>
<table width='100%'>
    <tr>
        <td colspan=2 height='24px' valign='middle'>
            <img src='/static/BULL1A.GIF'/>
            <b>今日热点</b>　<a href='news.php'><font size='2'>更多&gt;&gt;</font></a>
        </td>
    </tr>
    <tr><td colspan=2 height='6px'></td></tr>
    <?php $news10 = array_slice($news, 0, 10); foreach($news10 as $item){ ?>
    <tr>
        <td width='10px'></td>
        <td><img src='/static/BULLET3.GIF'/> <a href='newsDetail.php?key=<?=$item['detail_key']?>'><?=$item['title']?></a></td>
    </tr>
    <?php } ?>
</table><p align='center'><img src='/static/CONTLINE.GIF'></p>
<?php } ?>
<?php if($blogs){ ?>
<table width='100%'>
    <tr>
        <td colspan=2 height='24px' valign='middle'>
            <img src='/static/BULL1A.GIF'/>
            <b>我的博客</b>　<a href='blog/index.htm'><font size='2'>更多&gt;&gt;</font></a>
        </td>
    </tr>
    <tr><td colspan=2 height='6px'></td></tr>
    <?php foreach($blogs as $item){ ?>
    <tr>
        <td width='10px'></td>
        <td><img src='/static/BULLET3.GIF'/> <a href='blog/<?=$item['link']?>'><?=$item['title']?></a></td>
    </tr>
    <?php } ?>
</table><p align='center'><img src='/static/CONTLINE.GIF'></p>
<?php } ?>
</td></tr>
<tr><td height='10px'></td></tr>
</table></body></html>

