<!DOCTYPE html>
<html>
<%
from langpack import lang;
from util import pager;
import config;
PAGE_SIZE = config.PAGESIZE;
totalPages = int(total/PAGE_SIZE);
if (total % PAGE_SIZE):
	totalPages += 1;
end
if page > totalPages:
	page = totalPages;
end
%>
	<head>
		<meta charset='UTF-8'/>
		<title>{{lang('iNews')}}{{!lang('_title_spacer')}}</title>
	</head>
	<body>
		<table width='100%'><tr>
			<td width='50%'><h1>{{lang('iNews')}}</h1></td>
			<td align='right'><a href='/'>[{{lang('Back Home Page')}}]</a></td>
		</tr></table>
		<ul>
% for news in newsList:
			<li><a href='/news/{{news['id']}}'>{{news['title']}}</a></li>
% end
		</ul>
		{{!pager('/inews', 'page', totalPages, page)}}
	</body>
</html>
