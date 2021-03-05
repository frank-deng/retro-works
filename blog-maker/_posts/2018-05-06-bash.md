---
layout: post
title: Bash使用技巧
tags: [Linux, Shell]
---

---

从终端运行GUI程序
-----------------

从终端以后台方式运行GUI程序，并抑制标准输出和标准错误输出。

	(gui_program &>/dev/null &)

`gui_program`是运行GUI程序相关的命令。

---

从给定文件名中获取基本名和扩展名
--------------------------------

基本名：`BASENAME="${FILENAME%.*}";`  
扩展名：`EXTENSION="${FILENAME##*.}";`

---

按行遍历标准输出
----------------

	IFS=$'\n';
	for LINE in `ls`; do
		#Do some works on "${LINE}"
	done;

---

遍历带空格的命令行参数
----------------------

	while [ -n "${1}" ]; do
		FILENAME="${1}";
		#Do some works on "${FILENAME}"
		shift 1;
	done;

---

如何使用Perl的rename工具进行批量重命名
--------------------------------------

去除`.bak`扩展名：

	prename 's/\.bak$//' *

将文件名转换成小写：

	prename 'y/A-Z/a-z/' *

为`.txt`文件加前缀：

	prename 's/(.*).txt$/prefix_$1.txt/' *.txt

ArchLinux上需要安装`perl-rename`包来获得该工具。

---

如何找出带BOM头的文本文件
-------------------------

使用`find`命令和`file`命令：

	find . -type f -exec file {} \; | grep BOM

在bash shell中使用`grep`命令：

	grep -rlI $'^\xEF\xBB\xBF' .
	
排除特定扩展名的文件（可用于跳过二进制文件和大文件）：

	grep -rlI $'^\xEF\xBB\xBF' --exclude=*.bin --exclude=*.dat .
	find . -type f -not \( -ipath '*.bin' -o -ipath '*.dat' \) -exec file {} \; | grep BOM
	
排除`.svn`目录：

	grep -rlI $'^\xEF\xBB\xBF' --exclude-dir=.svn .
	find . -type f -not \( -ipath '*.svn*' \) -exec file {} \; | grep BOM

---

将视频转换成兼容HTML5的格式
---------------------------

	ffmpeg -i INPUT_FILE -c:v libx264 -crf 18 -c:a aac -q:a 100 -strict experimental OUTPUT.mp4

---

调整VIM的制表符宽度
-------------------

将以下内容加入到`/etc/vim/vimrc`中：

	set tabstop=4
	set softtabstop=4
	set shiftwidth=4
	
	" 使用空格代替tab字符
	set expandtab


---

使用gzip备份文件，并为备份文件名添加日期后缀
--------------------------------------

	gzip -kS ".$(date '+%Y%m%d_%H%M').gz" backup_file

---

