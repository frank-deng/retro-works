<!DOCTYPE html>
<html>
% from langpack import lang;
	<head>
		<meta charset='UTF-8'/>
		<title>{{joke['title']}} - {{lang('Jokes Collection')}}</title>
	</head>
	<body>
		<h1>{{joke['title']}}</h1>
		<p>{{joke['text']}}</p>
	</body>
</html>
