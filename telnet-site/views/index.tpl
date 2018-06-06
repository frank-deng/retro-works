<!DOCTYPE html>
<html>
<%
import datetime
from langpack import lang;
now = datetime.datetime.now();
dateStr = now.strftime(lang('_date_format'));
weekStr = lang('_week_format')[now.weekday()];
%>
	<head>
		<meta charset='UTF-8'/>
		<title>{{lang('Index')}} - {{dateStr}}&nbsp;{{weekStr}}{{!lang('_title_spacer')}}</title>
	</head>
	<body>
		<table width='100%'>
			<tr>
				<td width='100%' align='center'><!--
					-->｜<a href='/news'>{{lang('News')}}</a><!--
					-->｜<a href='/inews'>{{lang('iNews')}}</a><!--
					-->｜<a href='/jokes'>{{lang('Jokes')}}</a><!--
					-->｜<a href='/dict'>{{lang('Dictionary')}}</a><!--
					-->｜<a href='/currency'>{{lang('Currency Exchange')}}</a><!--
					-->｜</td>
			</tr>
			<tr><td colspan='2'>
% if weather:
{{weather['basic']['city']}}&nbsp;{{weather['now']['cond']['txt']}}&nbsp;{{weather['daily_forecast'][0]['tmp']['min']}}{{lang('Centidegree')}}/{{weather['daily_forecast'][0]['tmp']['max']}}{{lang('Centidegree')}}
% try:
{{lang('AQI')}}{{weather['aqi']['city']['aqi']}} {{weather['aqi']['city']['qlty']}}
% except KeyError:
%	pass;
% end
<a href='/weather/detail.do'>[{{lang('Weather Detail')}}]</a>
% else:
{{lang('No Weather Information')}}
% end
				<a href='weather/setcity.do'>[{{lang('Change City')}}]</a>
				<b><hr/></b>
			</td></tr>
		</table>
		<ul>
% for a in articles:
			<li><a href='/article/{{a['id']}}'>{{a['title']}}</a></li>
% end
		</ul>
		<div><a href='/articles'><b>{{lang('More Articles')}}&gt;&gt;</b></a></div>
	</body>
</html>

