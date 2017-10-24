<!DOCTYPE html>
<html>
% from langpack import lang;
% from util import pager;
	<head>
		<meta charset='UTF-8'/>
		<title>{{lang('Jokes Collection')}}</title>
	</head>
	<body>
		<table width='100%'><tr>
			<td width='60%'><h1>{{lang('Jokes Collection')}}</h1></td>
			<td align='right'><a href='/'>[{{lang('Back Home Page')}}]</a></td>
		</tr></table>
		<ul>
% for content in jokes:
			<li><a href='/jokes/{{content['id']}}'>{{content['title']}}</a></li>
% end
		</ul>
		{{!pager('/jokes', 'page', totalPages, page)}}
	</body>
</html>
