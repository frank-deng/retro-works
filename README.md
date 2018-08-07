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
![2048](http://frank-deng.github.io/retro-works/screenshots/2048_1.png)

2048游戏 2048 Game  
![2048](http://frank-deng.github.io/retro-works/screenshots/2048_2.png)

2048游戏（使用UCDOS特显程序） 2048 Game (Use Special Display utility from UCDOS)  
![2048](http://frank-deng.github.io/retro-works/screenshots/2048C_1.png)

2048游戏（使用UCDOS特显程序） 2048 Game (Use Special Display utility from UCDOS)  
![2048](http://frank-deng.github.io/retro-works/screenshots/2048C_2.png)

猜数字游戏 Bulls and Cows  
![Bulls and Cows](http://frank-deng.github.io/retro-works/screenshots/guessnum.png)

俄罗斯方块 Tetris  
![Tetris](http://frank-deng.github.io/retro-works/screenshots/Tetris_1.png)

俄罗斯方块 Tetris  
![Tetris](http://frank-deng.github.io/retro-works/screenshots/Tetris_2.png)

俄罗斯方块 Tetris  
![Tetris](http://frank-deng.github.io/retro-works/screenshots/Tetris_3.png)

条形图 Bar Chart  
![Bar Chart](http://frank-deng.github.io/retro-works/screenshots/barchart.png)

饼图 Pie Chart  
![Pie Chart](http://frank-deng.github.io/retro-works/screenshots/piechart.png)

求1000以内的质数 Get prime numbers under 1000  
![Prime Numbers](http://frank-deng.github.io/retro-works/screenshots/primes.png)

显示杨辉三角 Display Yanghui Triangle  
![Yanghui Triangle](http://frank-deng.github.io/retro-works/screenshots/Yanghui.png)

绘制几何形状 Drawing Geometric Shapes  
![Shapes](http://frank-deng.github.io/retro-works/screenshots/Shapes.png)

数独求解程序 Sudoku Solver  
![Sudoku](http://frank-deng.github.io/retro-works/screenshots/sudoku.png)

简单统计程序 Simple Statistics Program  
![Statistics](http://frank-deng.github.io/retro-works/screenshots/stat.png)

简单统计程序（使用中文界面） Simple Statistics Program with Chinese UI  
![Statistics](http://frank-deng.github.io/retro-works/screenshots/stat2.png)

条形图（使用UCDOS特显程序） Bar Chart (Use Special Display utility from UCDOS)  
![UCDOS Bar Chart](http://frank-deng.github.io/retro-works/screenshots/barchart2.png)

饼图（使用UCDOS特显程序） Pie Chart (Use Special Display utility from UCDOS)  
![UCDOS Pie Chart](http://frank-deng.github.io/retro-works/screenshots/piechart2.png)

使用UCDOS特显程序显示大尺寸汉字 Use Special Display utility from UCDOS to display Chinese characters in large size  
![Poem](http://frank-deng.github.io/retro-works/screenshots/poem.png)

UCDOS特显程序中可用的颜色 Colors available in the Special Display utility from UCDOS  
![256 Colors](http://frank-deng.github.io/retro-works/screenshots/256color.png)  
UCDOS使用VESA.DRV显示驱动后，可以显示上图中的256种颜色。（默认的VGA显示驱动只显示最上面一行的16种颜色）  
When UCDOS is started with VESA.DRV display driver, it will be capable of displaying the 256 colors above. (Default VGA.DRV can only display 16 colors in the first row)

UCDOS特显程序中可用的字体 Fonts available in the Special Display utility from UCDOS  
![Fonts](http://frank-deng.github.io/retro-works/screenshots/fonts.png)

屏保 Screensaver  
![Screensaver](http://frank-deng.github.io/retro-works/screenshots/lines.png)

屏保（使用UCDOS特显程序） Screensaver (Use Special Display utility from UCDOS)  
![Screensaver](http://frank-deng.github.io/retro-works/screenshots/lines2.png)


telnet-site
-----------

一个简单的telnet站点，使用[w3m](http://w3m.sourceforge.net)浏览器在字符界面下显示HTML页面。  
A simple site designed for console-based browser [w3m](http://w3m.sourceforge.net), which makes it works like an old-school telnet BBS site.

### 截图欣赏 Screenshots

![Telnet 1](http://frank-deng.github.io/retro-works/screenshots/telnet1.png)

![Telnet 2](http://frank-deng.github.io/retro-works/screenshots/telnet2.png)

![Telnet 3](http://frank-deng.github.io/retro-works/screenshots/telnet3.png)

![Telnet 4](http://frank-deng.github.io/retro-works/screenshots/telnet4.png)

![Telnet 5](http://frank-deng.github.io/retro-works/screenshots/telnet5.png)

![Telnet 6](http://frank-deng.github.io/retro-works/screenshots/telnet6.png)

### Linux服务器端配置 Linux Server Configuration

在`/etc/locale.gen`中加上`zh_CN.GB2312`，然后运行`sudo locale-gen`。  
Add `zh_CN.GB2312` into `/etc/locale.gen`, then run `sudo locale-gen`.

执行以下命令：  
Execute the following commands:

	sudo apt-get install w3m ncurses-term tcpser
	sudo pip install bottle httplib2 markdown
	sudo cp telnet-site/telnetd.py telnet-site/telnetLogin.py -t /usr/local/bin
	cp telnet-site/config.telnetsite telnet-site/keymap.telnetsite -t ~/.w3m
	cd ~/.w3m
	mv config config.bak ; mv keymap keymap.bak
	mv config.telnetsite config ; mv keymap.telnetsite keymap

在`/etc/crontab`中加入以下命令，实现开机时自动启动`telnetd.py`和`tcpser`：  
Add the following command to `/etc/crontab`, so as to start `telnetd.py` on boot:

	@reboot frank	/usr/local/bin/telnetd.py -H 127.0.0.1 -P 2333 -L /usr/local/bin/telnetLogin.py
	@reboot frank   /usr/bin/tcpser -v 6401 -s 19200 -n"92163=127.0.0.1:2333"

### Windows 3.x客户端使用方法 Windows 3.x Client Usage

打开“附件”程序组里的“终端仿真程序”，将使用的串口设为COM1，并将号码设为“92163”或“1270000000012333”，然后开始拨号，拨号成功后按Enter键进入登录界面。  
Open "Terminal Emulator" in the "Accessories" program group, set the serial port to use as "COM1", set phone number as 92163 or 1270000000012333, then start dialing. When dialing succeed, press `Enter` to open login panel.


实用命令 Useful Commands
-----------------------

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

	ffmpeg -i input.mp4 -c:v cinepak -c:a adpcm_ima_wav -vf scale=320:240 -ac 1 -ar 32000 -r 15 -y output.avi

DOSBox使用的Autoexec命令，用于挂载原始硬盘镜像和软盘镜像  
DOSBox autoexec command for mounting raw harddisk image and floppy image

	@imgmount 0 /home/frank/.dosbox/floppy.img -fs none
	@imgmount 2 /home/frank/.dosbox/dos620jp.img -fs none -t hdd -size 512,63,16,X


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

### 如何在Windows 3.x下安装S3显卡驱动 How to install S3 video driver for Windows 3.x

安装Windows 3.x时使用标准VGA显示驱动，安装完成后在“Windows 设置程序”中更改显卡驱动。  
Use the basic VGA driver for the initial install, then change the video driver using Windows Setup in the Main program group.

安装显卡驱动时如果提示插入S3 Trio 64V Flat Mode Driver软盘，则此时需要将路径填写成`C:\WINDOWS\SYSTEM\`以完成显卡驱动的安装。  
When the driver spouted up a prompt to Insert the Trio 64V Flat Mode Driver disk, redirect the installer to `C:\WINDOWS\SYSTEM\` to complete the graphics driver install.

