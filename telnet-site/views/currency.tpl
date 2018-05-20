<!DOCTYPE html>
<html>
%from langpack import lang;
	<head>
		<meta charset='UTF-8'/>
		<title>{{lang('Currency Exchange')}} - Powered By：易源接口</title>
	</head>
	<body>
		<table width='100%'><tr>
			<td width='50%'><h1>{{lang('Currency Exchange')}}</h1></td>
			<td align='right'><a href='/'>[{{lang('Back Home Page')}}]</a></td>
		</tr></table>
		<form action='/currency' method='post'>
			<input type='text' name='amount' size='16' value='{{amount}}'/><!--
			--><select name='from'>
% for currency in currencies:
% if fromCurrency == currency['code']:
% selected = 'selected=\'selected\'';
% else:
% selected = '';
% end
				<option value="{{currency['code']}}" {{selected}}>
					{{currency['code']+' '+currency['name']}}
				</option>
% end
			</select>
			{{lang('Exchange')}}
			<select name='to'>
% for currency in currencies:
% if toCurrency == currency['code']:
% selected = 'selected=\'selected\'';
% else:
% selected = '';
% end
				<option value="{{currency['code']}}" {{selected}}>
					{{currency['code']+' '+currency['name']}}
				</option>
% end
			</select>
			<input type='submit' value='{{lang('Query')}}'/>
		</form>
		<br/>
		<p>
% if hasResult:
% if None == result:
{{lang('Query Failed')}}
% else:
{{amount}} {{fromCurrencyName}} = {{result}} {{toCurrencyName}}
% end
% else:
&nbsp;
% end
		</p>
		<h2><hr/>{{lang('Realtime Exchange Rate')}}</h2>
		<table>
			<tr>
				<th align='left'>{{lang('Currency Code')}}</th>
				<th align='left'>{{lang('Currency Name')}}</th>
				<th align='left'>{{lang('hui_in')}}</th>
				<th align='left'>{{lang('chao_in')}}</th>
				<th align='left'>{{lang('hui_out')}}</th>
				<th align='left'>{{lang('chao_out')}}</th>
				<th align='left'>{{lang('zhesuan')}}</th>
			</tr>
% for currency in currencies:
				<tr>
					<td>{{currency['code']}}</td>
					<td>{{currency['name']}}</td>
					<td>{{currency['hui_in']}}</td>
					<td>{{currency['chao_in']}}</td>
					<td>{{currency['hui_out']}}</td>
					<td>{{currency['chao_out']}}</td>
					<td>{{currency['zhesuan']}}</td>
				</tr>
% end
		</table>
	</body>
</html>
