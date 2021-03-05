---
layout: post
title: Web开发技巧
tags: [HTML, JavaScript]
---

---

`htmlspecialchars()`的JavaScript实现
------------------------------------

	function htmlspecialchars(s){
		var M={'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'};
		return s.replace(/[&<>"']/g,function(m){return M[m]});
	}

---

通过User Agent获取浏览器类型
----------------------------

	function deviceType() {
		var ua = window.navigator.userAgent;
		if (/iphone|android.*mobile/i.test(ua)) {
			return 'mobile';
		} else if (/ipad|android/i.test(ua)) {
			return 'pad';
		}
		return undefined;
	}

手机浏览器返回`mobile`，平板浏览器返回`pad`，PC浏览器和其它类型的浏览器返回`undefined`。

---

Chrome for Android中更改地址栏的颜色
------------------------------------

将以下标签加到HTML的head标签中，就可以改变Chrome for Android的地址栏颜色了。

	<meta name="theme-color" content="#db5945"/>

---

如何在浏览器中捕获JS的语法错误
------------------------------

	window.addEventListener('error',function(e){
	    alert(e.filename+'\nLine '+e.lineno+'\n'+e.message);
	});

---

如何解决PDO-MySQL的乱码问题
---------------------------

使用如下DSN初始化PDO-MySQL连接：

	$dsn='mysql:dbname=sausagedb;host=127.0.0.1;charset=utf8'
	$dbconn = new PDO($dsn, $user, $password);

上面的DSN中包含`charset=utf8`，用于指定MySQL所使用的字符集为UTF-8。

如果连接数据库时不设置字符集，即使MySQL表的字符集是UTF-8，插入到MySQL表中的内容也将变为乱码。

---

使用QPython测试WebView
----------------------

新建一个Python脚本，代码如下：

	#qpy:3
	#qpy:webapp:Title
	#qpy://127.0.0.1:8080

`#qpy:webapp:Title`用于设置WebView的标题。

`#qpy://127.0.0.1:8080`用于设置WebView中打开的URL。

在上述代码末尾添加`#qpy:fullscreen`可以使WebView以全屏方式打开。

---

如何使用DOM元素作为按钮的提示
-----------------------------

如果需要将某个DOM元素作为按钮的提示，并不影响按钮的操作，可以为该DOM添加以下样式：

	pointer-events:none;

---

Vue.js加载可递归使用的组件（WebPack方式）
-----------------------------------------

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


