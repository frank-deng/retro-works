<!DOCTYPE html>
<html>
% from langpack import lang;
	<head>
		<meta charset='UTF-8'/>
		<title>{{lang('Dictionary')}}</title>
	</head>
	<body>
		<table width='100%'><tr>
			<td width='50%'><h1>{{lang('Dictionary')}}</h1></td>
			<td align='right'><a href='/'>[{{lang('Back Home Page')}}]</a></td>
		</tr></table>
		<form action='/dict' method='get'>
			<input type='text' name='word' size='30' value="{{word}}"/><input type='submit' value="{{lang('Query Dictionary')}}"/>
		</form><br/>
% if word:
% if None == result:
			<p>{{lang('Query Failed')}}</p>
% elif 'Not Found' == result:
			<p>{{lang('Not Found')}}</p>
% else:
			<p>{{lang('Meaning')}}</p>
			<ul><li>{{result['trans']}}</li></ul>
% if len(result['sentence']) > 0:
			<p>{{lang('Sentence Example')}}</p>
			<ol>
% for s in result['sentence']:
				<li><p>{{s['orig']}}<br/>{{s['trans']}}</p></li>
% end
			</ol>
% end
% if len(result['refer']) > 0:
			<p>{{lang('See Also')}}</p>
			<ul><li>
% for rel in result['refer']:
				<a href="/dict?word={{rel}}">{{rel}}</a>&nbsp;
% end
			</li></ul>
% end
% end
		<p><hr/><center>{{!lang('_about_dict')}}</center></p>
	</body>
</html>

