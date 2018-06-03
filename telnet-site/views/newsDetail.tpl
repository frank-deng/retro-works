<!DOCTYPE html>
<html>
% from langpack import lang;
	<head>
		<meta charset='UTF-8'/>
		<title>{{news['title']}}{{!lang('_title_spacer')}}</title>
	</head>
	<body>
		<h1>{{news['title']}}</h1>
		<p>{{news['date']}}</p>
% for line in news['content']:
		<p>{{line}}</p>
% end
	</body>
</html>
