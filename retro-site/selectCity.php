<?php
require('config.php');

$_TITLE=$_HEADER='天气预报';

mb_internal_encoding('UTF-8');
mb_http_output('GB2312');
mb_language('uni');
mb_regex_encoding('UTF-8');
ob_start('mb_output_handler');
header('content-type: text/html; charset=GB2312');

apcu_delete('weather_data');

$_QUERY=array();
foreach(explode('&',file_get_contents("php://input")) as $item){
    $kv=explode('=',$item);
    $key=$kv[0]; $value=$kv[1];
    switch($key){
        case 'city':
            $value=iconv('GB2312','UTF-8',rawurldecode($value));
        break;
    }
    $_QUERY[$key]=$value;
}

$city=$_QUERY['city'];
$cityData=null;
if($city){
    $ch=curl_init();
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
    curl_setopt($ch, CURLOPT_TIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
    curl_setopt($ch, CURLOPT_POST, 0);
    curl_setopt($ch, CURLOPT_URL, 'https://geoapi.qweather.com/v2/city/lookup?'.http_build_query([
        'key'=>$_CONFIG['HEWEATHER_KEY'],
        'location'=>$city
    ]));
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, FALSE);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, FALSE);
    curl_setopt($ch, CURLOPT_ENCODING, 'UTF-8');
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    try{
        $data=curl_exec($ch);
        $cityData=json_decode($data,true)['location'];
    }catch(Exception $e){
        error_log($e);
    }
    curl_close($ch);
}

require('header.php');
?><form method='post'>
请输入城市：<input type='text' name='city' value='<?=$city?>'><input type='submit' value='搜索'><hr>
</form>
<?php if($cityData){ ?>
<h3>请选择城市</h3>
<ul>
<?php foreach($cityData as $item){ 
    $name=$item['adm1'].'-'.$item['adm2'];
    if($item['name']!=$item['adm2']){
        $name.='-'.$item['name'];
    }
    $value=$item['id'].';'.$name;
?>
    <li><a href='weather.php?location=<?=$value?>'><?=$name?></a></li>
<?php } ?>
</ul>
<?php }
require('footer.php');

