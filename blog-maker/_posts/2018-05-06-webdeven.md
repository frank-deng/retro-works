---
layout: post
title: Web Development Skills
tags: [HTML, JavaScript]
---

---

Implement `htmlspecialchars()` in JavaScript
--------------------------------------------

	function htmlspecialchars(s){
		var M={'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'};
		return s.replace(/[&<>"']/g,function(m){return M[m]});
	}

---

Get browser type based on User Agent
------------------------------------

	function deviceType() {
		var ua = window.navigator.userAgent;
		if (/iphone|android.*mobile/i.test(ua)) {
			return 'mobile';
		} else if (/ipad|android/i.test(ua)) {
			return 'pad';
		}
		return undefined;
	}

This function returns `mobile` for mobile browsers, `pad` for tablet browsers. `undefined` for PC browsers or browsers of other type.

---

Change address bar color of Chrome for Android
----------------------------------------------

Add the following meta tag into HTML to change address bar color of Chrome for Android.

	<meta name="theme-color" content="#db5945"/>

---

Catching Syntax Error Within Browser
------------------------------------

	window.addEventListener('error',function(e){
	    alert(e.filename+'\nLine '+e.lineno+'\n'+e.message);
	});

---

How to solve the PDO-MySQL's garbled data problem
-------------------------------------------------

Use the following DSN to initialize PDO-MySQL connection:

	$dsn='mysql:dbname=sausagedb;host=127.0.0.1;charset=utf8'
	$dbconn = new PDO($dsn, $user, $password);

The DSN above contains `charset=utf8`, which specifies UTF-8 as the character set used for MySQL.

Without specifing character set for database connection, you will find the data inserted into the MySQL table garbled, even if the MySQL table's character set is UTF-8.

---

Use QPython to test WebView
---------------------------

Create a python script with the following code:

	#qpy:3
	#qpy:webapp:Title
	#qpy://127.0.0.1:8080

`#qpy:webapp:Title` specifies the title of the WebView.

`#qpy://127.0.0.1:8080` specifies the URL launched in the WebView.

Append `#qpy:fullscreen` to the code above will enable fullscreen mode for the WebView.

---

CSS Style For DOM-Based Tooltip
-------------------------------

Apply the following style to the DOM element used for tooltip, so that normal mouse operations won't be inteferred:

	pointer-events:none;

---

Vue.js Load Component Which Can Be Used Recursively
---------------------------------------------------

	export default{
		...
		components:{
			...
			leaf:()=>import('path/to/leaf.vue'),
			...
		},
		...
	}

---

