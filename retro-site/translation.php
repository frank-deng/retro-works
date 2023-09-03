<?php
require('common.php');

$_TITLE=$_HEADER='在线翻译';

$_QUERY=array();
foreach(explode('&',$_SERVER['QUERY_STRING']) as $item){
    $kv=explode('=',$item);
    $key=$kv[0]; $value=$kv[1];
    switch($key){
        case 'word':
            $value=iconv('GB2312','UTF-8',rawurldecode($value));
            $value=str_replace('+',' ',$value);
        break;
    }
    $_QUERY[$key]=$value;
}

$word=$_QUERY['word'];
if (!$word) {
    $_QUERY['dir']='en-zh';
} else {
    $access_token=GetAccessToken($_CONFIG['TRANSLATION_KEY'][0], $_CONFIG['TRANSLATION_KEY'][1]);
    if ($access_token){
        $dir=explode('-',$_QUERY['dir']);
        $ch=curl_init();
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
        curl_setopt($ch, CURLOPT_TIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
        curl_setopt($ch, CURLOPT_POST, 1);
        curl_setopt($ch, CURLOPT_URL, 'https://aip.baidubce.com/rpc/2.0/mt/texttrans/v1?access_token='.$access_token);
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, FALSE);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, FALSE);
        curl_setopt($ch, CURLOPT_ENCODING, 'UTF-8');
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_HTTPHEADER, array(
            'Content-Type: application/json',
            'Accept: application/json'
        ));
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode(array(
            'from' => $dir[0],
            'to' => $dir[1],
            'q' => $word,
        )));
        $resp=curl_exec($ch);
        curl_close($ch);
        $result=json_decode($resp,true);
    }
}

require('header.php');
?><form action='translation.php' method='get'>
请输入单词：<input type='text' name='word' value='<?=$word?>'> <?php
?><label for='radio-en-zh'><input type='radio' name='dir' id='radio-en-zh' value='en-zh' <?=('en-zh'==$_QUERY['dir'] ? 'checked' : '')?>>英→中</label> <?php
?><label for='radio-zh-en'><input type='radio' name='dir' id='radio-zh-en' value='zh-en' <?=('zh-en'==$_QUERY['dir'] ? 'checked' : '')?>>中→英</label> <?php
?><input type='submit' value='翻译'><hr>
</form>
<?php if ($result) { ?>
<h3><font <?=$dir[0]=='en' ? 'face="Times New Roman"' : '' ?>><?=$result['result']['trans_result'][0]['src']?></font></h3>
<ul>
    <li><font <?=$dir[1]=='en' ? 'face="Times New Roman"' : '' ?>><?=$result['result']['trans_result'][0]['dst']?></font>
</ul>
<?php } ?>
<?php
require('footer.php');
