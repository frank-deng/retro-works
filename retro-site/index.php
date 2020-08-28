<?php require('config.php');
?><html>
	<head>
		<meta charset='GB2312'/>
		<title>首页 - {{dateStr}} {{weekStr}}</title>
	</head>
	<body topmargin='0' leftmargin='0' rightmargin='0' bottommargin='0' bgcolor='#ffffff' background='static/GRAY.JPG'>
    <table width='100%' cellspacing='0'>
      <!--页头和天气模块-->
      <tr>
        <td bgcolor='#ffff33' width='10px' rowspan='100'></td>
        <td bgcolor='#ffff33' bordercolor='#ff0000' rowspan='2' width='50%' height='40px' nowrap>
          <img src='/static/CONTBULL.GIF'/><font size='5' color='#000080'><b>欢迎光临我的信息港</b>&nbsp;</font><img src='static/CONTBULL.GIF'/></td>
        <td bgcolor='#ffff33' bordercolor='#ff0000' nowrap align='right' width='50%'>\\
% if weather:
{{weather['basic']['city']}}&nbsp;{{weather['now']['cond']['txt']}}&nbsp;{{weather['daily_forecast'][0]['tmp']['min']}}{{lang('Centidegree')}}/{{weather['daily_forecast'][0]['tmp']['max']}}{{lang('Centidegree')}}\\
 % try:
&nbsp;{{lang('AQI')}}{{weather['aqi']['city']['aqi']}} {{weather['aqi']['city']['qlty']}}\\
 % except KeyError:
  %	pass;
 % end
% end
</td>
        <td bgcolor='#ffff33' width='10px' rowspan='100'></td>
      </tr>
      <tr>
        <td bgcolor='#ffff33' align='right' height='16px'><font size='2'>|
<?php foreach($_CONFIG['LINKS'] as $item){ ?><a href='{{item["link"]}}'>{{item['title']}}</a> |<?php } ?>
% if weather:
          <a href='/weather/detail.do'>{{lang('Weather Detail')}}</a> |<?php } ?>
</font></td>
      </tr>
      <!--新闻模块-->
      <tr><td colspan='2' height='5px'></td></tr>
% if news:
      <tr><td colspan='2'><table width='100%'>
        <tr>
          <td colspan='2' height='24px' valign='middle'>
            <img src='/static/BULL1A.GIF'/>
            <b>{{lang('Today News')}}</b>　<a href='/news'><font size='2'>{{lang('View News Detail')}}&gt;&gt;</font></a></td>
          <td width='5px' rowspan='100'></td>
        </tr>
        <tr><td height='5px'></td></tr>\\
% for item in news:
        <tr>
          <td width='10px'></td>
          <td><img src='/static/BULLET3.GIF'/> {{item['title']}}</td>
        </tr>
% end
      </table></td></tr>
% end
      <tr><td colspan='2' height='28px' align='center'>
        <img src='/static/CONTLINE.GIF'/>
      </td></tr>
      <tr><td colspan='2' bgcolor='#ffff33' height='8px'></td></tr>
    </table></body></html>
