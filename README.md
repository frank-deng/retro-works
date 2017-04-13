Retro Programming Works 怀旧编程作品
====================================

一些古董平台上的编程作品，仅供娱乐。  
Some retro programming works for some old platforms, just for fun.

GW-BASIC
--------

一个类似1980年代家用电脑上的BASIC编程环境。  
A BASIC environment similar to those on home computers in 1980's.

因为该语言的[诸多缺陷](http://www.cnbeta.com/articles/deep/232400.htm)，导致代码难以维护，故该语言仅用于简单计算，或编写猜数字、2048之类的小游戏。  
However, due to the [limitations](http://programmingisterrible.com/post/40132515169/dijkstra-basic) of this programming language, the code for this language is very hard to maintain, so it's only used for simple calculations, small games like *Bulls and Cows* and *2048*.

telnet-site
-----------

一个简单的telnet站点，使用[w3m](http://w3m.sourceforge.net)浏览器在字符界面下显示HTML页面。
A simple site designed for console-based browser [w3m](http://w3m.sourceforge.net), which makes it works like an old-school telnet BBS site.

DOSBox模拟的客户端硬件  
Client side hardware emulated by DOSBox

* Old 386 platform
* VGA display
* Floppy drive only
* Virtual serial modem with Hayes command set

客户端使用的软件  
Client side software

* MS-DOS 5.0
* ANSI.SYS
* UCDOS 7.0
* NRDTERM.EXE

TX-fun
------

使用UCDOS自带的特显程序，以显示不同字体和字号的中文，并绘制一些简单的图表。  
An environment use `TX.COM` shipped along with UCDOS to display Chinese characters in different sizes and fonts, as well as drawing some simple graphs.

可用的程序  
Applications available

* 飞控中心 (Flight Information Center)
* 猜数字控制台 (Control center for Bulls and Cows AI)
* 2048控制台 (Control center for 2048 AI)

DOSBox模拟的客户端硬件  
Client side hardware emulated by DOSBox

* Old 386 platform
* Hercules Monochrome display
* Floppy drive only
* Virtual serial line connection

客户端使用的软件  
Client side software

* MS-DOS 5.0
* UCDOS 7.0
* COMTOOL.COM

Notes 
-----

Convert raw disk image into VDI format image

	VBoxManage convertdd source.img destination.vdi --format VDI

Convert VDI format HDD image into raw one

	VBoxManage clonehd source.vdi destination.img --format RAW

