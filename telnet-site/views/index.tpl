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
				<td width='40%'>{{now.strftime(lang('_date_format'))}} {{lang('_week_format')[now.weekday()]}}</td>
				<td width='60%' align='right'>｜<a href='/dict'>{{lang('Dictionary')}}</a>｜<a href='/currency'>{{lang('Currency Exchange')}}</a>｜</td>
			</tr>
			<tr><td colspan='2'>
% if weather:
{{weather['basic']['city']}}
{{weather['now']['cond']['txt']}}
{{weather['daily_forecast'][0]['tmp']['min']}}{{lang('Centidegree')}}/{{weather['daily_forecast'][0]['tmp']['max']}}{{lang('Centidegree')}}
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
				<hr/><div><b>{{lang('Up To Date')}}</b>&nbsp;<a href='/news'>{{lang('More')}}&gt;&gt;</a></div>
% if None == news:
				<p>{{lang('No News')}}</p>
% else:
				<ul>
% for n in news:
				<li><a href='/news/detail/{{n['newsid']}}'>{{n['title']}}</a></li>
% end
				</ul>
% end

% if None != movieRank:
				<hr/><div><b>{{lang('Movie Rank')}}</b></div>
				<table width='100%'>
					<tr>
						<th align='left' width='33%'><b>{{lang('Daily Rank')}}</b></th>
						<th align='left' width='33%'><b>{{lang('Weekend Rank')}}</b></th>
						<th align='left' width='33%'><b>{{lang('Weekly Rank')}}</b></th>
					</tr>
					<tr>
						<td valign='top'><ol>
% if None != movieRank['weekly']:
% for movie in movieRank['weekly']:
							<li>{{movie['MovieName']}}</li>
% end
% end
						</ol></td>
						<td valign='top'><ol>
% if None != movieRank['daily']:
% for movie in movieRank['daily']:
							<li>{{movie['MovieName']}}</li>
% end
% end
						</ol></td>
						<td valign='top'><ol>
% if None != movieRank['weekend']:
% for movie in movieRank['weekend']:
							<li>{{movie['MovieName']}}</li>
% end
% end
						</ol></td>
					</tr>
				</table>
% end

				<hr/><div><b>{{lang('Jokes Collection')}}</b>&nbsp;<a href='/jokes'>{{lang('More')}}&gt;&gt;</a></div>
% if None == jokes:
				<p>{{lang('No Jokes')}}</p>
% else:
				<table width='100%'><tr>
					<td valign='top' width='50%'><ul>
% for i in range(5):
						<li><a href='jokes/{{jokes[i]['id']}}'>{{jokes[i]['title']}}</a></li>
% end
					</ul></td>
					<td valign='top' width='50%'><ul>
% for i in range(5,10):
						<li><a href='jokes/{{jokes[i]['id']}}'>{{jokes[i]['title']}}</a></li>
% end
					</ul></td>
				</tr></table>
% end

				<hr/><div><b>{{lang('My Space')}}</b>&nbsp;<a href='/articles'>{{lang('More')}}&gt;&gt;</a></div>
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

