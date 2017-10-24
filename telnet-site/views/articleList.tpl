<!DOCTYPE html>
<html>
<%
from langpack import lang;
from util import pager;
import config;
PAGE_SIZE = config.PAGESIZE;
totalPages = int(len(articles)/PAGE_SIZE);
if len(articles) % PAGE_SIZE:
	totalPages += 1;
end
if page > totalPages:
	page = totalPages;
end
articles = articles[(page-1)*PAGE_SIZE : (page)*PAGE_SIZE];
%>
	<head>
		<meta charset='UTF-8'/>
		<title>{{lang('My Space')}}</title>
	</head>
	<body>
		<table width='100%'><tr>
			<td width='50%'><h1>{{lang('My Space')}}</h1></td>
			<td align='right'><a href='/'>[{{lang('Back Home Page')}}]</a></td>
		</tr></table>
		<ul>
% for a in articles:
			<li><a href='/article/{{a['id']}}'>{{a['title']}}</a></li>
% end
		</ul>
		{{!pager('/articles', 'page', totalPages, page)}}
	</body>
</html>
