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
![Sudoku](http://frank-deng.github.io/retro-works/screenshots/Chengfa.png)

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

显示古诗 Poem Showing  
![Poem](http://frank-deng.github.io/retro-works/screenshots/poem.png)

新年快乐 Happy New Year  
![Happy New Year](http://frank-deng.github.io/retro-works/screenshots/New_Year.png)

显示古诗（使用UCDOS特显程序） Poem Showing (Using UCDOS Special Display Tool)  
![Poem for UCDOS](http://frank-deng.github.io/retro-works/screenshots/Poem_UCDOS.png)

新年快乐（使用UCDOS特显程序） Happy New Year (Using UCDOS Special Display Tool)  
![Happy New Year for UCDOS](http://frank-deng.github.io/retro-works/screenshots/New_Year_UCDOS.png)


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
* 打字练习 Typing training
* 五笔打字练习 Wubi input training


### 1997's PC

配置 Configuration

* CPU 80486SX 33MHz
* 8M RAM
* 256M HDD
* S3 864 Graphics Adapter with 384k VRAM, capable of handling 640x480 256-color video mode.
* CD-ROM
* Sound Blaster 16
* Mouse
* 33.6k Modem

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

	ffmpeg -i input.mp4 -c:v cinepak -c:a adpcm_ima_wav -vf scale=320:240 -ac 1 -ar 32000 -r 15 -y output.avi

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

