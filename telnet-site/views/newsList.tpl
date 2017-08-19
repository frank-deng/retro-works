<!DOCTYPE html>
<html>
<%
from langpack import lang;
from util import pager;
if None == channel:
channelName = lang('Up To Date');
searchLink = '/news';
else:
channelName = channel['name'];
searchLink = '/news/'+channel['id'];
end
%>
	<head>
		<meta charset='UTF-8'/>
		<title>{{channelName}}</title>
	</head>
	<body>
			<table width='100%'>
				<tr>
					<td width='40%'><b>{{channelName}}</b>&nbsp;<a href='/news/channels'>{{lang('Select Channel')}}&gt;&gt;</a></td>
					<td align='right'>
						<form href='{{searchLink}}'>
							<input type='text' name='keyword' size='20' value="{{keyword}}"/><input type='submit' value='{{lang('Search')}}'/><!--
							-->{{lang('_sep')}}<!--
							--><a href='/'>[{{lang('Back Home Page')}}]</a>
						</form>
					</td>
				</tr>
			</table>
			<ul>
% for n in news:
				<li><a href="/news/{{n['newsid']}}">{{n['title']}}</a></li>
% end
			</ul>
			{{!pager(searchLink, 'page', totalPages, page)}}<br/>
		<?php } ?>
	</body>
</html>
