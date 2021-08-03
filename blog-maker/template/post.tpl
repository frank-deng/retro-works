<html>
  <head>
		<meta name='viewport' id='viewport' content='width=device-width,initial-scale=1.0,minimum-scale=1.0,maximum-scale=1.0,user-scalable=no'/>
    <% if(encoding){ %>
      <meta charset='<%=encoding%>'/>
    <% } %>
    <% if(title){ %>
      <title><%=title%></title>
    <% } %>
  </head>
  <body bgcolor='#ffffff'>
    <h1 align='center'><%-titleProcessed%></h1>
    <%-content%>
  </body>
</html>
