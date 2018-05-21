<!DOCTYPE html>
<html>
% import re;
% from langpack import lang;
	<head>
		<meta charset='UTF-8'/>
		<title>{{weather['basic']['city']}}{{lang('Weather')}} - Powered by：和风全球天气{{!lang('_title_spacer')}}</title>
	</head>
	<body>
		<table width='100%'><tr>
			<td width='50%'>
				<b>{{weather['basic']['city']}}{{lang('Weather')}}</b>
				<a href='/weather/setcity.do'>[{{lang('Change City')}}]</a>
			</td>
			<td align='right'><a href='/'>[{{lang('Back Home Page')}}]</a></td>
		</tr></table>
		<table>
			<tr>
				<th align='left'>{{lang('Weather')}}</th>
				<th align='left'>{{lang('Temperature')}}</th>
				<th align='left'>{{lang('Humidity')}}</th>
				<th align='left'>{{lang('UVLevel')}}</th>
				<th align='left'>{{lang('Visibility')}}</th>
				<th align='left'>{{lang('Wind Direction')}}</th>
				<th align='left'>{{lang('Wind Speed')}}</th>
				<th align='left'>{{lang('AQI2')}}</th>
				<th align='left'>{{lang('AQILevel')}}</th>
			</tr>
			<tr>
				<td>{{weather['now']['cond']['txt']}}</td>
				<td>{{weather['daily_forecast'][0]['tmp']['min']}}{{lang('Centidegree')}}/{{weather['daily_forecast'][0]['tmp']['max']}}{{lang('Centidegree')}}</td>
				<td>{{weather['daily_forecast'][0]['hum']}}%</td>
				<td>{{weather['daily_forecast'][0]['uv']}}</td>
				<td>{{weather['daily_forecast'][0]['vis']}} km</td>
				<td>{{weather['daily_forecast'][0]['wind']['dir']}}</td>
				<td>
% sc = weather['daily_forecast'][0]['wind']['sc'];
% if re.match(r'[\d]', sc):
{{sc}}级
% else:
{{sc}}
% end
</td>
% try:
				<td>{{weather['aqi']['city']['aqi']}}</td>
				<td>{{weather['aqi']['city']['qlty']}}</td>
% except KeyError:
%	pass;
% end
		</table>
		<h2>{{lang('More Forecast')}}</h2>
		<table>
			<tr>
				<th align='left'>{{lang('Date')}}</th>
				<th align='left'>{{lang('Weather')}}</th>
				<th align='left'>{{lang('Temperature')}}</th>
				<th align='left'>{{lang('Humidity')}}</th>
				<th align='left'>{{lang('UVLevel')}}</th>
				<th align='left'>{{lang('Visibility')}}</th>
				<th align='left'>{{lang('Wind Direction')}}</th>
				<th align='left'>{{lang('Wind Speed')}}</th>
			</tr>
% for i in range(len(weather['daily_forecast'])-1):
% forecast = weather['daily_forecast'][i+1];
				<tr>
					<td>{{forecast['date']}}</td>
					<td>{{forecast['cond']['txt_d']}}/{{forecast['cond']['txt_n']}}</td>
					<td>{{forecast['tmp']['min']+lang('Centidegree')}}/{{forecast['tmp']['max']+lang('Centidegree')}}</td>
					<td>{{forecast['hum']}}%</td>
					<td>
% if int(forecast['uv']) >= 0:
{{forecast['uv']}}
%end
</td>
					<td>
% if int(forecast['vis']) >= 0:
{{forecast['vis']}} km
%end
</td>
					<td>{{forecast['wind']['dir']}}</td>
					<td>
% sc = forecast['wind']['sc'];
% if re.match(r'[\d]', sc):
{{sc}}级
% else:
{{sc}}
% end
</td>
				</tr>
% end
		</table>

		<h2>{{lang('Weather Suggestion')}}</h2>
		<ul>
% for key in weather['suggestion']:
% sugg = weather['suggestion'][key];
		<li><p><b>{{lang('_suggestion')[key]}}</b> {{sugg['brf']}}<br/>{{sugg['txt']}}</p></li>
% end
		</ul>
	</body>
</html>

