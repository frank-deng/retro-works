Retro Programming Works 怀旧编程作品
====================================

一些古董平台上的编程作品。仅供娱乐。  
Some retro programming works for some vintage platforms. For entertainment use only.

BASIC
-----

一些基于DOS下QBASIC上的作品。  
Some works based on QBASIC under DOS.

因其支持结构化编程，使得程序的开发、维护更加方便。  
Thanks to QBASIC's support of structured programming, development and maintenance is much easier.

部分程序需要DOS方式下的中文系统（如UCDOS），以正确显示汉字。  
Some programs require DOS-based Chinese system (e.g. UCDOS) to display Chinese characters properly.

部分程序需要UCDOS下自带的特显程序`TX.COM`和UCDOS的轮廓字库，以实现UCDOS下的绘图操作，并以正确的字形显示大尺寸字符。  
Some programs require UCDOS's special display utility `TX.COM` and outline fonts for UCDOS, so as to enable graphic drawing under UCDOS, as well as displaying large-sized characters in correct glyph.

### 截图欣赏 Screenshots

2048游戏 2048 Game  
![2048](http://frank-deng.github.io/retro-works/screenshots/2048.png)

猜数字游戏 Bulls and Cows  
![Bulls and Cows](http://frank-deng.github.io/retro-works/screenshots/guessnum.png)

九九乘法表 9x9 Multiplication Table  
![Multiplication Table](http://frank-deng.github.io/retro-works/screenshots/Chengfa.png)

求1000以内的质数 Get prime numbers under 1000  
![Prime Numbers](http://frank-deng.github.io/retro-works/screenshots/primes.png)

显示杨辉三角 Display Yanghui Triangle  
![Yanghui Triangle](http://frank-deng.github.io/retro-works/screenshots/Yanghui.png)

条形图 Bar Chart  
![Bar Chart](http://frank-deng.github.io/retro-works/screenshots/barchart.png)

饼图 Pie Chart  
![Pie Chart](http://frank-deng.github.io/retro-works/screenshots/piechart.png)

俄罗斯方块 Tetris  
![Tetris](http://frank-deng.github.io/retro-works/screenshots/Tetris.png)

绘制几何形状 Drawing Geometric Shapes  
![Shapes](http://frank-deng.github.io/retro-works/screenshots/Shapes.png)

屏保 Screensaver  
![Screensaver](http://frank-deng.github.io/retro-works/screenshots/lines.png)

谢尔宾斯基地毯 Sierpinski Carpet  
![Sierpinski Carpet](http://frank-deng.github.io/retro-works/screenshots/Carpet.png)

显示古诗 Poem Showing  
![Poem](http://frank-deng.github.io/retro-works/screenshots/poem.png)

显示古诗（使用BSAVE图像数据） Poem Showing (Using BSAVE Image Data)  
![Poem 2](http://frank-deng.github.io/retro-works/screenshots/poem2.png)

新年快乐 Happy New Year  
![Happy New Year](http://frank-deng.github.io/retro-works/screenshots/New_Year.png)

显示古诗（使用UCDOS特显程序） Poem Showing (Using UCDOS Special Display Tool)  
![Poem for UCDOS](http://frank-deng.github.io/retro-works/screenshots/Poem_UCDOS.png)

显示带插图的古诗（使用UCDOS特显程序） Poem With Picture (Using UCDOS Special Display Tool)  
![Poem for UCDOS](http://frank-deng.github.io/retro-works/screenshots/Poem2_UCDOS.png)

新年快乐（使用UCDOS特显程序） Happy New Year (Using UCDOS Special Display Tool)  
![Happy New Year for UCDOS](http://frank-deng.github.io/retro-works/screenshots/New_Year_UCDOS.png)

2048游戏（使用UCDOS特显程序） 2048 Game (Using UCDOS Special Display Tool)  
![Happy New Year](http://frank-deng.github.io/retro-works/screenshots/2048_UCDOS.png)

UCDOS特显程序256色列表 256-Color Table of UCDOS Special Display Tool  
![Color Table](http://frank-deng.github.io/retro-works/screenshots/TX.png)

Retro-Site
----------

一个简单的HTML站点，主要兼容IE3浏览器，并配有类似Jekyll的静态博客网站生成器。  
A simple HTML site optimized for IE3 browser, equipped with a Jekyll-like static blog site generator.

PPP服务器和静态博客网站生成器需要在Linux环境（如Debian、Ubuntu）中运行。  
PPP Server and static blog site generator require running under Linux environments like Debian, Ubuntu.

### Linux服务器端配置 Linux Server Configuration

执行以下命令安装所需软件：  
Execute the following commands to install softwares required:

	sudo apt-get install python3 pppd nginx-light php-fpm php-mbstring
	sudo cp pppd.py /usr/local/bin

`pppd.py`可以在代码库中的`misc`目录里找到。  
`pppd.py` can be found at `misc` folder in this repository.

在`/etc/crontab`中加入以下命令，实现开机时自动启动`pppd.py`和`tcpser`：  
Add the following command to `/etc/crontab`, so as to start `pppd.py` and `tcpser` on boot:

	@reboot root /usr/local/bin/pppd.py -H 127.0.0.1 -P 2333 defaultroute mtu 576 10.0.2.15:192.168.7.2 noauth

其中`192.168.7.2`是DOSBox中的PPP拨号客户端使用的IP；`10.0.2.15`则是主机或目标站点的IP。  
`192.168.7.2` is the IP address used by PPP client inside DOSBox, while `10.0.2.15` is the IP address of the host machine or the target site.

### DOSBox串口配置 Configure DOSBox's Serial Interface

在`dosbox-x.conf`所在目录中添加`phonebook.txt`，内容如下：  
Create `phonebook.txt` at the same directory of `dosbox-x.conf`:

	12345 127.0.0.1:2333

将DOSBox配置中`[serial]`小节下的配置项做如下修改：  
Change DOSBox configuration under seciton `[serial]`:

	serial1 = modem
	phonebookfile = phonebook.txt

### Windows 3.x客户端使用方法 Windows 3.x Client Usage

设置新的PPP连接时需要将电话号码设置成`12345`，IP地址设置成`192.168.7.2`，用户名和密码为空。  
When setting up new PPP connection, set phone number with `12345`, set IP address with `192.168.7.2`, leave username and password blank.

检查“使用远程网上的默认网关”选项是否被选中，否则将无法连接目标服务器。  
Check whether "Use default gateway on remote network" box is checked, or you'll be unable to connect to the target server.

当连接成功时，打开浏览器，使用URL`http://目标站点IP`访问目标站点。  
When connection established, open browser and use URL `http://Target IP` to access the target site.

### 配置博客生成器 Configure Blog Maker

执行以下命令安装所需的软件：  
Execute the following commands to install the softwares required:

	sudo apt-get install nodejs imagemagick inkscape

然后进入`blog-maker`目录运行`npm start`即可生成博客站点内容，生成结果在`dist`目录中。  
Then enter `blog-maker` directory and run `npm start` to generate the blog site, generated files can be found at `dist` directory.

### 截图欣赏 Screenshots

天气预报 Weather Forecast  
![Weather Forecast](http://frank-deng.github.io/retro-works/screenshots/retro-site_1.png)

我的博客 My Blog  
![My Blog](http://frank-deng.github.io/retro-works/screenshots/retro-site_2.png)

带数学公式的文章 Article with Equation  
![Math](http://frank-deng.github.io/retro-works/screenshots/retro-site_3.png)


Telnet-Server
-------------

一个简单的telnet服务器，可以使用Telix、HyperTerminal之类的客户端通过串口进行连接。  
A simple telnet server, which can be connected via serial port using softwares like Telix, HyperTerminal.

服务端需要执行以下命令安装所需的软件：  
Execute the following commands to install the softwares required at server side:

	sudo apt-get install nodejs ncurses-term


被模拟的PC Emulated PCs
-----------------------

### 1992's PC

配置 Configuration

* V30 (80186 Compatible) CPU
* 640k RAM
* 5.25" 1.2M High Density Floppy Drive
* 5.25" 360k Double Side Floppy Drive
* CGA Display Adapter with green monochrome monitor

主要用途 Main Usage

* 中英文文字处理 Chinese & English text processing
* BASIC编程 BASIC Programming
* 俄罗斯方块游戏 Tetris game
* 2048游戏 2048 Game
* 英文打字练习 English typing training
* 五笔打字练习 Wubi input training

### 1997's PC

配置 Configuration

* CPU 80486DX 66MHz
* 8M RAM
* 256M HDD
* S3 864 Graphics Adapter with 384k VRAM, capable of handling 640x480 256-color video mode.
* CD-ROM
* Sound Blaster 16
* Mouse
* 56k Modem

主要用途 Main Usage

* 英语学习 English learning
* 英汉字典 English-Chinese dictionary
* 中英文文字处理 Chinese & English text processing
* BASIC编程 BASIC Programming
* 多媒体光盘浏览 Viewing multimedia CDs
* 图片浏览 Image viewing
* 音乐播放 Music playback
* 视频播放 Video playback
* 拨号上网 Surfing online via dial-up network
* 拨号连接远程服务器 Connecting to remote server via dial-up network
* （禁止游戏 NO GAMING）


实用命令 Useful Commands
------------------------

将原始硬盘镜像转换成VDI格式硬盘镜像  
Convert raw disk image into VDI format image

	VBoxManage convertdd source.img destination.vdi --format VDI

将VDI格式硬盘镜像转换成原始硬盘镜像  
Convert VDI format HDD image into raw HDD image

	VBoxManage clonehd source.vdi destination.img --format RAW

Linux下挂载虚拟软盘（使用GB2312编码的文件名）  
Mount floppy image under Linux (Use GB2312 for filename encoding)

	sudo mount -o loop,codepage=936,iocharset=utf8 floppy.img /mnt

使用ffmpeg制作可在Windows 3.1下播放的视频  
Convert video into format accepted by Windows 3.1

	ffmpeg -i input.mp4 -c:v cinepak|msvideo1 -c:a pcm_s16le|pcm_u8|adpcm_ima_wav\
		-vf "scale=320:240:force_original_aspect_ratio=decrease,pad=320:240:(ow-iw)/2:(oh-ih)/2"\
		-r 12 -ac 1 -ar 22050 -y output.avi

DOSBox使用的Autoexec命令，用于挂载原始硬盘镜像和软盘镜像  
DOSBox autoexec command for mounting raw harddisk image and floppy image

	@imgmount 0 /home/frank/.dosbox/floppy.img -fs none
	@imgmount 2 /home/frank/.dosbox/hdd.img -fs none -t hdd -size 512,63,16,X


### 如何在Windows 3.x下安装S3显卡驱动 How to install S3 video driver for Windows 3.x

安装Windows 3.x时使用标准VGA显示驱动，安装完成后在“Windows 设置程序”中更改显卡驱动。  
Use the basic VGA driver for the initial install, then change the video driver using Windows Setup in the Main program group.

安装显卡驱动时如果提示插入S3 Trio 64V Flat Mode Driver软盘，则此时需要将路径填写成`C:\WINDOWS\SYSTEM\`以完成显卡驱动的安装。  
When the driver spouted up a prompt to Insert the Trio 64V Flat Mode Driver disk, redirect the installer to `C:\WINDOWS\SYSTEM\` to complete the graphics driver install.

### X11禁止Ctrl+Alt+Fn键切换终端 Disable Switching TTY Via Ctrl+Alt+Fn Under X11

将以下内容添加到`/etc/xorg.conf`：  
Add the following code to `/etc/xorg.conf`:

	Section "ServerFlags"
	    Option "DontVTSwitch" "true"
	EndSection

### 启用Linux的串口终端 Enable serial console under Linux

临时为`/dev/ttyS0`启用串口登录（重启后失效）：  
Temporarily enable serial console on `/dev/ttyS0` (Disabled after reboot):

    systemctl start getty@ttyS0.service

永久为`/dev/ttyS0`启用串口登录：  
Permanently enable serial console on `/dev/ttyS0`:

    systemctl enable serial-getty@ttyS0.service

查看`/dev/ttyS0`的串口登录功能是否启用：  
Check whether serial console is enabled on `/dev/ttyS0`:

    systemctl status serial-getty@ttyS0.service

