<!DOCTYPE html>
<html>
<%
from langpack import lang;
%>
	<head>
		<meta charset='UTF-8'/>
		<title>{{jokes[page-1]['title']}} - {{lang('Jokes')}}{{!lang('_title_spacer')}}</title>
	</head>
	<body>
		<table width='100%'>
			<tr>
				<td width='50%'><b>{{lang('Jokes')}}</b></td>
				<td align='right'>
% if page > 1:
<a href='/jokes?page={{page-1}}'>{{lang('Prev One')}}</a>
% end
% if page < len(jokes):
&nbsp;<a href='/jokes?page={{page+1}}'>{{lang('Next One')}}</a>
% end
&nbsp;<a href='/'>[{{lang('Back Home Page')}}]&nbsp;</a>
				</td>
			</tr>
			<tr><td width='100%' colspan='2'><b><hr/></b></td></tr>
		</table>
% joke = jokes[page-1]
		<h2>{{joke['title']}}</h2>
		<p>{{!'<br/>'.join(joke['content'])}}</p>
	</body>
</html>
