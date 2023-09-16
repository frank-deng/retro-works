<?php
require('common.php');
require('Parsedown.php');
$Parsedown = new Parsedown();

$_TITLE=$_HEADER='你问我答';

$question=null;
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    foreach(explode('&',file_get_contents("php://input")) as $item){
        $kv=explode('=',$item);
        $key=$kv[0]; $value=$kv[1];
        switch($key){
            case 'question':
                $value=iconv('GB2312','UTF-8',rawurldecode($value));
                $value=str_replace('+',' ',$value);
            break;
        }
        $_POST[$key]=$value;
    }
    $question=$_POST['question'];
    if ($question) {
        $access_token=GetAccessToken($_CONFIG['ERINE_KEY'][0], $_CONFIG['ERINE_KEY'][1]);
        if ($access_token){
            $ch=curl_init();
            curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 30);
            curl_setopt($ch, CURLOPT_TIMEOUT, 30);
            curl_setopt($ch, CURLOPT_POST, 1);
            curl_setopt($ch, CURLOPT_URL, 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token='.$access_token);
            curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, FALSE);
            curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, FALSE);
            curl_setopt($ch, CURLOPT_ENCODING, 'UTF-8');
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
            curl_setopt($ch, CURLOPT_HTTPHEADER, array(
                'Content-Type: application/json'
            ));
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode([
                'messages'=>[
                    [
                        'role'=>'user',
                        'content'=>$question
                    ]
                ]
            ]));
            $resp=curl_exec($ch);
            curl_close($ch);
            $result=json_decode($resp,true);
        }
    }
}

require('header.php');
?><form action='ask.php' method='post' valign='top'>
<table width='100%' cellspacing='0' cellpadding='0'>
    <tr><td colspan=2 height='24px' valign='top'>请输入问题：</td></tr>
    <tr>
        <td valign='top'><textarea type='text' name='question' cols='60' rows='3'><?=$question?></textarea></td>
        <td valign='top' width='100%'><input type='submit' value='提问'></td>
    </tr>
    <tr><td colspan=2><hr></td></tr>
</table>
</form>
<?php if ($result) { ?>
<h5>以下是相关回答：</h5>
<p><?=$Parsedown->text($result['result'])?></p>
<?php } ?>
<?php
require('footer.php');
