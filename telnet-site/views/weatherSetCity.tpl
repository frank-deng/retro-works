<!DOCTYPE html>
<html>
% from langpack import lang;
	<head>
		<meta charset='UTF-8'/>
		<title>{{lang('Change City')}}</title>
	</head>
	<body>
		<h1>{{lang('Change City')}}</h1>
		<form action='/weather/setcity.do' method='post'>
			<input type='text' name='city' value="{{city}}"/><input type='submit' value="{{lang('OK')}}"/>
		</form>
		<p><hr/><center><a href='/'>[{{lang('Back Home Page')}}]</a></center></p>
	</body>
</html>
