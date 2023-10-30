<?php
require('common.php');

$_TITLE=$_HEADER='在线翻译';
$result=$text=null;

$question=null;
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    foreach(explode('&',file_get_contents("php://input")) as $item){
        $kv=explode('=',$item);
        $key=$kv[0]; $value=$kv[1];
        switch($key){
            case 'text':
                $value=iconv('GB2312','UTF-8',rawurldecode($value));
                $value=str_replace('+',' ',$value);
            break;
        }
        $_POST[$key]=$value;
    }
    $text=$_POST['text'];
    $from='en';
    $to='zh';
    if ($_POST['zh_to_en']){
        $from='zh';
        $to='en';
    }

    if ($text) {
        $access_token=GetAccessToken($_CONFIG['TRANSLATION_KEY'][0], $_CONFIG['TRANSLATION_KEY'][1]);
        if ($access_token){
            $ch=curl_init();
            curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 30);
            curl_setopt($ch, CURLOPT_TIMEOUT, 30);
            curl_setopt($ch, CURLOPT_POST, 1);
            curl_setopt($ch, CURLOPT_URL, 'https://aip.baidubce.com/rpc/2.0/mt/texttrans/v1?access_token='.$access_token);
            curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, FALSE);
            curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, FALSE);
            curl_setopt($ch, CURLOPT_ENCODING, 'UTF-8');
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
            curl_setopt($ch, CURLOPT_HTTPHEADER, array(
                'Content-Type: application/json'
            ));
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
                'from'=>$from,
                'to'=>$to,
                'q'=>$text
            ]));
            $resp=curl_exec($ch);
            curl_close($ch);
            $result=json_decode($resp,true);
        }
    }
}

require('header.php');
?><form action='translation.php' method='post' valign='top'>
<table width='100%' cellspacing='0' cellpadding='0'>
    <tr><td colspan=2 height='24px' valign='top'>请输入内容：</td></tr>
    <tr>
        <td valign='top'><textarea type='text' name='text' cols='58' rows='3'><?=$text?></textarea></td>
	<td valign='top' width='100%'>
            <input type='submit' name='zh_to_en' value='中翻英'><br/>
            <input type='submit' name='en_to_zh' value='英翻中'></td>
    </tr>
    <tr><td colspan=2><hr></td></tr>
</table>
</form>
<?php if ($result) { ?>
<h5>以下是翻译结果：</h5>
<font face="<?=($to=='zh' ? '宋体' : 'Times New Roman')?>"><?php foreach($result['result']['trans_result'] as $item){ ?><p><?=$item['dst']?></p></font><?php } ?>
<?php } ?>
<?php
require('footer.php');
