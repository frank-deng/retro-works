Retro Programming Works 怀旧编程作品
====================================

一些古董平台上的编程作品。仅供娱乐。  
Some retro programming works for some old platforms. Just for fun.

GW-BASIC
--------

一个类似1980年代家用电脑上的BASIC编程环境。  
A BASIC environment similar to those on home computers in 1980's.

因为该语言的[诸多缺陷](http://www.cnbeta.com/articles/deep/232400.htm)，导致代码难以维护，故该语言仅用于简单计算，或编写猜数字、2048之类的小游戏。  
However, due to the [limitations](http://programmingisterrible.com/post/40132515169/dijkstra-basic) of this programming language, make the code very hard to maintain, so it's only used for simple calculations, small games like *Bulls and Cows* and *2048*.

### 截图欣赏 Screenshots

![Startup](http://frank-deng.github.io/retro-works/Startup.png)

![Prime Numbers](http://frank-deng.github.io/retro-works/Prime%20Numbers.png)

![Bulls and Cows](http://frank-deng.github.io/retro-works/Guessnum.png)

![2048](http://frank-deng.github.io/retro-works/2048-1.png)

![2048](http://frank-deng.github.io/retro-works/2048-2.png)

![Graph](http://frank-deng.github.io/retro-works/Graph.png)

![Chinese Demo](http://frank-deng.github.io/retro-works/Chinese.png)

![Shapes](http://frank-deng.github.io/retro-works/Shapes.png)


QBASIC
------

一些DOS下的QBASIC上的作品。  
Some works based on QBASIC under DOS.

因其支持结构化编程，使得程序的开发、维护更加方便。  
Thanks to QBASIC's support of structured programming, development and maintenance is much easier.

部分程序需要DOS方式下的中文系统（如UCDOS），以正确显示汉字。  
Some programs require DOS-based chinese system (e.g. UCDOS) to display chinese characters properly.

`GUSHI.BAS`、`TUBIAO.BAS`、`TXDEMO.BAS`需要UCDOS下自带的特显程序`TX.COM`和UCDOS的轮廓字库，以实现UCDOS下的绘图操作，并以正确的字体显示大尺寸汉字。  
`GUSHI.BAS`, `TUBIAO.BAS`, `TXDEMO.BAS` require UCDOS's special display utility `TX.COM` and outline fonts for UCDOS, so as to enable graphic drawing under UCDOS, as well as displaying large-sized chinese characters in correct glyph.


telnet-site
-----------

一个简单的telnet站点，使用[w3m](http://w3m.sourceforge.net)浏览器在字符界面下显示HTML页面。  
A simple site designed for console-based browser [w3m](http://w3m.sourceforge.net), which makes it works like an old-school telnet BBS site.

### 截图欣赏 Screenshots

![Telnet 1](http://frank-deng.github.io/retro-works/telnet1.png)

![Telnet 2](http://frank-deng.github.io/retro-works/telnet2.png)

### Linux服务器端配置 Linux Server Configuration

在`/etc/locale.gen`中加上`zh_CN.GB2312`，然后运行`sudo locale-gen`。  
Add `zh_CN.GB2312` into `/etc/locale.gen`, then run `sudo locale-gen`.

安装需要的软件包  
Install package needed

	sudo apt-get install ncurses-term tcpser
	sudo pip install bottle httplib2 markdown
	
将`telnetd.py`和`mylogin.py`复制到`/usr/local/bin`目录中。  
Copy `telnetd.py` and `mylogin.py` to directory `/usr/local/bin`.

将`config.telnetsite`文件和`keymap.telnetsite`文件复制到`~/.w3m`目录中，然后将`config.telnetsite`更名为`config`，以禁止从`w3m`浏览器中运行外部命令，增强站点的安全性。  
Copy file `config.telnetsite` and `keymap.telnetsite` to folder `~/.w3m`, then rename `config.telnetsite` to `config`, so as to disable executing external commands from `w3m` browser, so as to enhance the safety of the site.

在`/etc/crontab`中加入以下命令，实现开机时自动启动`telnetd.py`和`tcpser`：  
Add the following command to `/etc/crontab`, so as to start `telnetd.py` on boot:

	@reboot frank	/usr/local/bin/telnetd.py -H 127.0.0.1 -P 2333 -L /usr/local/bin/mylogin.py
	@reboot frank   /usr/bin/tcpser -v 6401 -s 2400 -n"92163=127.0.0.1:23"

### Windows 3.x客户端使用方法 Windows 3.x Client Usage

打开“附件”程序组里的“终端仿真程序”，将使用的串口设为COM1，并将号码设为“92163”或“1270000000012333”，然后开始拨号，拨号成功后按Enter键进入登录界面。  
Open "Terminal Emulator" in the "Accessories" program group, set the serial port to use as "COM1", set phone number as 92163 or 1270000000012333, then start dialing. When dialing succeed, press `Enter` to open login panel.


Notes 
-----

将原始硬盘镜像转换成VDI格式硬盘镜像  
Convert raw disk image into VDI format image

	VBoxManage convertdd source.img destination.vdi --format VDI

将VDI格式硬盘镜像转换成原始硬盘镜像  
Convert VDI format HDD image into raw one

	VBoxManage clonehd source.vdi destination.img --format RAW

Linux下挂载虚拟软盘（使用GB2312编码的文件名）  
Mount floppy image under Linux (Use GB2312 for filename encoding)

	sudo mount -o loop,codepage=936,iocharset=utf8 floppy.img /mnt

使用ffmpeg制作Windows 3.1下播放的视频  
Convert video into format accepted by Windows 3.1

	ffmpeg -i input.mp4 -c:v cinepak -c:a adpcm_ima_wav -vf scale=320:240 -ac 1 -ar 32000 -r 15 -y output.avi
