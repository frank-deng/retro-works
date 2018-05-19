<!DOCTYPE html>
<html>
<%
import datetime
from langpack import lang;
%>
	<head>
		<meta charset='UTF-8'/>
		<title>{{lang('Index')}}</title>
	</head>
	<body>
		<table width='100%'>
			<tr>
% now = datetime.datetime.now();
				<td width='40%'>{{now.strftime(lang('_date_format'))}}&nbsp;{{lang('_week_format')[now.weekday()]}}</td>
				<td width='60%' align='right'>｜<a href='/dict'>{{lang('Dictionary')}}</a>｜<a href='/currency'>{{lang('Currency Exchange')}}</a>｜</td>
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
			</td></tr>
			<tr><td colspan='2'>
				<hr/><div><b>{{lang('Articles')}}</b>&nbsp;<a href='/articles'>{{lang('More')}}&gt;&gt;</a></div>
				<ul>
% for a in articles:
					<li><a href='/article/{{a['id']}}'>{{a['title']}}</a></li>
% end
				</ul>
				<hr/><div>{{!lang('About')}}</div>
			</td></tr>
		</table>
	</body>
</html>

