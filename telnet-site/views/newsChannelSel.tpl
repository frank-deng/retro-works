<!DOCTYPE html>
<html>
% from langpack import lang;
% DISPLAY_ROWS=5;
	<head>
		<meta charset='UTF-8'/>
		<title>{{lang('Select Channel')}}</title>
	</head>
	<body>
		<h1>{{lang('Select Channel')}}<hr/></h1>
		<table width='100%'>
			<tr>
% for idx,channel in enumerate(channelsAll):
% if channel[0] == '0':
% destUrl = '/news';
% else:
% destUrl = '/news/'+channel[0];
% end
				<td width='{{100/DISPLAY_ROWS}}%'><a href="{{destUrl}}">{{channel[1]}}</a></td>
% if (idx % DISPLAY_ROWS) == (DISPLAY_ROWS - 1):
				</tr><tr>
% end
% end
			</tr>
		</table>
	</body>
</html><?php
