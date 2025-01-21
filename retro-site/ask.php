<?php
require('common.php');
require('Parsedown.php');
$Parsedown = new Parsedown();

$_TITLE=$_HEADER='你问我答';

$question=null;
$result=null;
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
            curl_setopt($ch, CURLOPT_URL, 'https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-speed-pro-128k?access_token='.$access_token);
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
                        'content'=>$question,
                        'temperature'=>0.01,
                        'top_p'=>0,
                    ]
                ]
            ]));
            $resp=curl_exec($ch);
            curl_close($ch);
            $result=json_decode($resp,true);
        }
    }
}
?><html>
<head>
  <meta charset='GB2312'/>
  <title><?=$_TITLE?></title>
</head>
<body topmargin='10px' leftmargin='10px' rightmargin='10px' bottommargin='10px' bgcolor='#ffffff'>
<h1 align='center'><img src='static/title.gif'></h1>
<form action='ask.php' method='post' valign='top'>
<table width='100%' cellspacing='0' cellpadding='0'>
    <tr><td colspan=2 height='24px' valign='top'><h5><font color='#00007f'>请输入问题：</font></h5></td></tr>
    <tr>
        <td valign='top'><textarea type='text' name='question' cols='58' rows='3'><?=$question?></textarea></td>
        <td valign='top' width='100%'><input type='submit' value='提问'></td>
    </tr>
    <tr><td colspan=2 height='24px' valign='top'><hr></td></tr>
</table>
</form>
<?php if ($result) { ?>
<h5><font color='#00007f'>以下是相关回答：</font></h5><?=$Parsedown->text($result['result'])?>
<p align='center'><hr></p>
<?php } ?>
<p align='center'><font face='Times New Roman'>E-Mail: <a href='mailto:niwenwoda@10.0.2.2'>niwenwoda@10.0.2.2</a></font></p>
</body></html>
