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

数独求解程序 Sudoku Solver  
![Sudoku Solver](http://frank-deng.github.io/retro-works/screenshots/Sudoku_Solver.png)

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

PPP服务器和Telnet服务器
----------------------

IE3浏览器可通过PPP协议访问部署在服务端的HTML站点，并配有类似Jekyll的静态博客网站生成器。  
IE3 browser can access the HTML site deployed at server side via PPP protocol. A Jekyll-like static blog site generator is also available.

Telnet服务器可使用类似Telix、HyperTerminal的终端仿真程序通过拨号方式连接。  
Use terminal emulators like Telix, HyperTerminal to dial to the Telnet server.

PPP服务器、Telnet服务器和静态博客网站生成器需要在Linux环境（如Debian、Ubuntu）中运行。  
PPP server, Telnet server and static blog site generator require running under Linux environments like Debian, Ubuntu.

**严禁将PPP服务器或Telnet服务器部署到生产环境或含有敏感数据的环境！！！**  
**DO NOT deploy PPP server or Telnet server to production environment or environment with sensitive data!!!**

### Linux PPP服务器和Telnet服务器配置 Linux PPP Server Configuration

执行以下命令安装所需软件：  
Execute the following commands to install softwares required:

	sudo apt-get install python3 pppd nginx-light php-fpm php-mbstring php-apcu
	cd telnet-ppp-server
	sudo python3 setup.py install

在`/etc/crontab`中加入以下命令，实现开机时自动启动PPP服务器和Telnet服务器：  
Add the following command to `/etc/crontab`, so as to start PPP server on boot:

	@reboot root /usr/local/bin/pppd.py -P 2333 multilink enable-session defaultroute ipcp-accept-remote mtu 576 10.0.2.15: noauth
	@reboot user /usr/local/bin/telnetd.py -P 2345 -c path/to/telnetd.conf

其中`10.0.2.15`是主机或目标站点的IP。  
`10.0.2.15` is the IP address of the host machine or the target site.

### DOSBox串口配置 Configure DOSBox's Serial Interface

在`dosbox-x.conf`所在目录中添加`phonebook.txt`，内容如下：  
Create `phonebook.txt` at the same directory of `dosbox-x.conf`:

	12345 127.0.0.1:2333
	16666 127.0.0.1:2345

将DOSBox配置中`[serial]`小节下的配置项做如下修改：  
Change DOSBox configuration under seciton `[serial]`:

	serial1 = modem
	phonebookfile = phonebook.txt

### VirtualBox NAT配置端口转发 Configure NAT Port Forwarding for VirtualBox

如果PPP服务器和Telnet服务器是部署在VirtualBox虚拟机里的Linux系统上，且虚拟机网卡连接的是NAT网络，则需要在虚拟机网卡的端口转发设置中为虚拟机里的PPP服务器和Telnet服务器分别添加2条端口转发规则，以使得主机上的DOSBox-X能访问虚拟机里的服务。
If PPP server and Telnet server are deployed on the VirtualBox Linux guest, and guest network adapter is attacted to NAT. Then you must add port forwarding rules for PPP server and Telnet server inside guest machine, so as to enable host DOSBox-x accessing them.

转发规则各个字段意义如下：  
Meanings of port forwarding rule columns:

* **名称 Name**  
可任意指定，也可以留空。  
Any value is acceptable, including blank value.
* **协议 Protocol**  
此处固定选择`TCP`（此处UDP没有使用）。  
Always select `TCP` here (UDP is unused here).
* **主机IP Host IP**  
可以不指定，也可以指定`127.0.0.1`以限制只有在主机上运行的程序可以访问对应的服务。  
Leave it blank, or specify `127.0.0.1` to limit only programs running on the host machine can access the service.
* **主机端口 Host Port**  
可任意指定一个主机上未使用的端口。  
Any port number not used on the host machine are acceptable.
* **子系统IP Guest IP**  
在虚拟机的Linux里使用`ip address`命令查看虚拟机网卡对应的IP地址，一般是`10.0.2.15`。  
Use command `ip address` inside Linux guest to get the IP address of the guest network card, in most cases it's `10.0.2.15`.
* **子系统端口 Guest Port**  
PPP服务器和Telnet服务器在虚拟机中使用的端口  
Port numbers of PPP server and Telnet server inside virtual machine.

虚拟机里的程序可以通过`虚拟路由器IP`+`主机上的服务对应的端口号`来访问主机上的服务。虚拟路由器IP可通过以下步骤获得：  
Programs inside virtual machine can access host services via `Virtual Router IP` + `port of the host service`. You can get the virtual router IP via the following steps:

1. 在虚拟机的Linux终端中输入`ip route show`命令。  
Execute command `ip route show` in the guest Linux terminal.
2. 在上一步的命令输出中找到`default via`后面的IP地址，该地址即为客户机的虚拟路由器IP，VirtualBox客户机中一般为`10.0.2.2`。  
Find out the IP address after `default via` from the output of the step above, this is the virtual router IP for the guest machine. For VirtualBox guests it's `10.0.2.2` in most cases.

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

* BASIC编程 BASIC Programming
* 中英文文字处理 Chinese & English text processing
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

* BASIC编程 BASIC Programming
* 英语学习 English learning
* 英汉字典 English-Chinese dictionary
* 英文打字练习 English typing training
* 中英文文字处理 Chinese & English text processing
* 电子表格和图表处理 Spreadsheet and chart processing
* 多媒体光盘浏览 Viewing multimedia CDs
* 图片浏览 Image viewing
* 音乐和视频播放 Music & video playback
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

