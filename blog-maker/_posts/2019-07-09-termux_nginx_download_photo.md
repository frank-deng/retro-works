---
layout: post
title: 如何用termux和nginx从手机上下载照片到电脑
tags: [Linux, Shell, Termux]
---

手机端准备
----------

手机上安装termux，然后在termux内安装nginx，使用命令：`pkg install nginx`。

nginx配置

	http {
	    include mime.types;
	    default_type application/octet-stream;
	    sendfile on;
	    keepalive_timeout 65;
	    server {
	        listen 8080;
	        server_name localhost;
	        charset utf-8;
	        location / {
	            root /sdcard/DCIM/Camera;
	            autoindex on;
	        }
	    }
	}

---

电脑端准备
----------

电脑上需要有wget，Windows版可以从[http://www.gnu.org/software/wget/](http://www.gnu.org/software/wget/)下载，然后解压。Linux一般自带该工具，无需另外安装。

连接
----

1. 确保手机和电脑连接的是同一wifi。
2. 在手机的WLAN设置中打开WLAN高级设置，找到当前手机在局域网里的IP地址。或在手机的设置功能中搜索“IP地址”亦可。
3. 在电脑端的浏览器里输入`http://IP地址:8080/`，如果看到类似文件列表的页面时，就说明连接成功了。

将照片下载到电脑
----------------

使用以下命令进行下载：

	wget -r -nH -nc -c -l 0 'http://IP地址:8080/'

