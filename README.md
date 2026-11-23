Retro Programming Works 怀旧编程作品
====================================

1998s PC
--------

“旧瓶装新酒”——一台想跟上时代，不想做孤岛的古董电脑。

<!--尽可能发挥Windows 3.2的潜力-->

### 配置

* 486 DX2-66MHz CPU
* 8M RAM
* 512M HDD
* S3 Graphics Adapter with 1M VRAM（Windows 3.2下支持640x480高彩色）
* 3.5 Inch Floppy Drive x1
* CD-ROM
* Sound Blaster 16
* Mouse
* NE2000（后期加装）

### 主要用途

* 文字处理（WPS 97、Word 6.0）
* 电子表格（Excel 5.0）
* 上网看新闻
* 收发邮件
* 连接远端UNIX机器
* FTP上传下载文件

### 安装说明

Windows 3.2的部署（附加组件取舍、声卡驱动）见“Windows 3.2部署说明”。

Windows 3.2推荐安装以下软件：

* WPS 97
* Microsoft Office 4.2（详细说明见“Microsoft Office 4.2安装说明”）
* 五笔字形输入法（绿色安装方案见“五笔字形输入法安装说明”）
* Trumpet Winsock
* Internet Explorer 3.0（仅安装浏览器）
* Tera Term/SimpTerm/Mocha Telnet/EWAN（通过Telnet连接远端站点）
* WS FTP16LE（FTP客户端）
* FoxMail（邮件客户端）

#### Windows 3.2部署说明

Windows 3.2安装时，安装所有附加组件，但以下附件不推荐安装：

* 对象包装程序及其帮助
* 记录器及其帮助
* 录音机及其帮助
* 造字程序及其帮助

Windows 3.2用的Sound Blaster 16驱动推荐安装精简版的，不带播放器和其它工具。

#### Microsoft Office 4.2安装说明

Microsoft Office 4.2可选组件非常多，部分组件存在功能冗余、中文乱码、稳定性差、实用价值低等问题，推荐安装的组件如下：

* Word除本体外，只安装“联机帮助、示例”中的“Word帮助”、“示例”
* Excel除本体外，“联机帮助和教程”中只安装“Microsoft Excel帮助”，加载宏中只安装“自动保存”
* Microsoft PowerPoint、Microsoft Office管理器不安装
* 共享应用程序中只安装“公式编辑器”
* “转换程序、过滤程序和数据存取”中，安装所有文字转换程序和图形过滤程序，“数据存取”不安装
* 工具中只安装“MS Info”
* 可选装长城全真中文字体

#### 五笔字形输入法安装说明

五笔字形输入法除了安装相关五笔输入法软件外，还可通过Windows 3.2自带的码表生成器实现。步骤如下：

* 打开码表生成器
* 加载并编译五笔码表文件（`misc/WB.TXT`）
* 在控制面板中的输入法设置中安装“通用码表输入法”，之后在输入法设置中选择“五笔字形”即可

### NE2000配置

需要准备DOS下的NE2000驱动和WINPKT驱动，以保证Windows 3.x下的Trumpet Winsock能正常使用NE2000网卡。

DOSBox-X需要在`dosbox-x.conf`中将NE2000的`backend`设置为`slirp`，然后在`[ethernet, slirp]`小节中进行以下设置：

	mtu                   = 1500
	mru                   = 1500
	ipv4_network          = 10.0.2.0
	ipv4_netmask          = 255.255.255.0
	ipv4_host             = 10.0.2.2
	ipv4_nameserver       = 8.8.8.8
	ipv4_dhcp_start       = 10.0.2.15

`AUTOEXEC.BAT`中添加以下命令：

	LH NE2000.COM 0x60 3 0x300
	LH WINPKT.COM 0x60

Trumpet Winsock中进行以下设置：

* 设置`IP address`为`10.0.2.15`
* 设置`Netmask`为`255.255.255.0`
* 设置`Default gateway`为`10.0.2.2`
* 设置`Packet vector`为`60`
* 设置`MTU`为`1500`
* 设置`TCP RWIN`和`TCP RSS`为`1460`

之后通过 `10.0.2.2`+端口号 即可访问DOSBox-X模拟器所在主机上的服务（主机上的服务可绑定`127.0.0.1`以限制仅本机可访问）。

### DNS配置

Linux主机端DNSmasq可使用以下配置：

	bind-interfaces
	no-resolv
	no-hosts
	server=8.8.8.8
	listen-address=10.0.2.15
	address=/mysite.com/10.0.2.2
	address=/www.mysite.com/10.0.2.2

### 补充说明

* 公式排版以Office 4.2自带的公式编辑器为主，因其需OLE，8M内存下建议将Windows 3.2永久交换文件开到16M以上；少量简单公式可用EQ域代码，现代Microsoft Word亦支持同款功能，但排版能力弱于公式编辑器。
* `retro-servers`目录中包含多个自制服务，用于和Windows 3.2中的Internet Explorer 3.0、FoxMail、WS\_FTP、Tera Term等软件对接。
* `retro-servers`中的自制服务，使用1024以下端口前需要执行`sudo setcap 'cap_net_bind_service=+ep' /usr/bin/python3`开启相关权限；`/usr/bin/python3`必要时需顺着软链接找到真正的可执行文件本身。
* 该机随时接受任何来自可信外部机器构建的程序，一般通过浏览器或FTP下载。
* Programmer's File Editor在Windows 3.2上无法输入中文，故不予安装。
* WinZip实测2037年之后不可用，如无压缩解压需要可不安装。
* Windows 3.2可实现拨号上网功能，详情请见[PPP\_Network.md](PPP_Network.md)

### AI时代的新用法

通过FoxMail的SMTP/POP3协议收发纯文本邮件，或使用`retro-servers`目录中提供的兼容Internet Explorer 3.0的纯HTML网页版邮件系统，可直接向现代大模型API问问题，并将大模型的回答以回复邮件的形式返回，可用于解答现实生活中的问题。


1990s PC
--------

用中文写文章的最小配置，汉字在信息时代浴火重生之纪念。

<!--除非绝对必要，不再新加任何软件，改动任何文件-->

### 配置

* CPU: 8088 8MHz
* RAM: 640k
* Floppy Drive A: 5.25" 360k Double Side
* Floppy Drive B: 5.25" 360k Double Side
* Display: Hercules Graphic Adapter with green monochrome monitor
* ISA RTC

### 主要用途

* WPS中英文文字处理，练习五笔打字
* BASIC编程
* 俄罗斯方块游戏
* 2048游戏

### 所用软盘说明

#### MS-DOS 3.3系统软盘

使用`FORMAT B: /S /8 /V`命令制作320k系统引导盘。

系统盘中推荐放入以下文件：

	ATTRIB.EXE
	AUTOEXEC.BAT
	CHKDSK.COM
	DEBUG.COM
	DISKCOMP.COM
	DISKCOPY.COM
	EDLIN.COM
	FC.EXE
	FIND.EXE
	FORMAT.COM
	GWBASIC.EXE
	LABEL.COM
	MORE.COM
	SORT.EXE
	SYS.COM
	TREE.COM
	XCOPY.EXE

`AUTOEXEC.BAT`内容如下：

	@ECHO OFF
	PATH A:
	ECHO.


#### CCDOS软盘

存放CCDOS汉字系统的基本程序和字库文件。

放入以下文件：

	CCDOS.BAT  （加载汉字系统的批处理文件）
	CCLIBJ.DOT （CCDOS 16点阵字库）
	CHLIB.COM  （CCDOS核心程序）
	HELP.TXT   （CCDOS常用按键帮助）
	QUIT.COM   （退出CCDOS）
	VDKEY.COM  （CCDOS核心程序）
	WBX.COM    （CCDOS五笔字形输入法）

`CCDOS.BAT`内容如下：

	@ECHO OFF
	CHLIB
	VDKEY
	WBX


#### 数据盘（常驻B驱动器）

除存放所有BASIC程序文件及其依赖数据、WPS文档外，推荐放入以下文件：

	PY.COM     （CCDOS拼音、双拼输入法）
	WPS.EXE    （WPS主程序）
	WPS1.OVL   （WPS依赖文件）
	WPS2.OVL   （WPS依赖文件）
	TETRIS.COM （俄罗斯方块游戏）

* 所有BASIC程序文件及其依赖数据可在本仓`BASIC`目录中找到。
* 所有WPS文档可在本仓`BASIC/DOC`目录中找到。


### 补充说明

* GW-BASIC限制较多，不支持结构化编程，只能使用行号，所有变量皆全局变量。因此开发前需仔细评估程序复杂度以决定是否移植到GW-BASIC上，开发时需严格控制`GOTO`的使用以保证一定程度的可维护性。
* WPS打开的文件包含GB2312不支持的字符时，极易出现死机。
* 本机使用Hercules显卡，此时GW-BASIC只支持文本模式，不支持任何图形模式。
* 该机纯展示向，暂定只保留现有软件阵容，不上线更多软件/程序。


1996s PC
---------

国内90年代一台典型的386机。

<!--除非绝对必要，不再新加任何软件，改动任何文件-->

### 配置

* 386 SX-33MHz CPU
* 2M RAM
* SVGA-Compatible Graphics Adapter with 512k VRAM（支持640x480 256色）
* 64M Hard Disk
* 3.5 Inch Floppy Drive x1
* 5.25 Inch Floppy Drive x1

### 主要用途

* WPS打字
* CCED制表、计算
* 汇编语言编程（仅限QBASIC程序依赖的汇编模块以及少数汇编程序）
* BASIC编程
* 英汉字典
* 图片浏览
* 俄罗斯方块、2048、贪吃蛇等小游戏

### 安装说明

推荐安装以下软件：

* UCDOS+宋体简、仿宋简、黑体简、楷体简轮廓字库和24点阵字库，外加12点阵宋体字库
* UCDICT（希望辞海，UCDOS和Windowa 3.x环境下均可用）
* CCED（简单数值计算、表格处理）
* SEA/PictView（看图软件）
* DAZZLE.EXE（DOS下的屏幕保护程序）
* TASM+TLINK（汇编器+连接器）
* Microsoft Scenes中的所有JPG图片

本机部署`BASIC`、`QB/DOC`、`QB`、`ASM`目录中所有文件。

### 补充说明

* 为保证可维护性，QBASIC建议将代码规模控制在600行以内。
* UCDOS WPS默认的蓝底绿字难以看清，可用`WPS /FE /S`命令改为更清楚的蓝底黄字。用`WPS /?`获取命令行帮助信息。
* UCDOS WPS模拟显示功能可使用Pause键暂停显示，然后按任意键继续模拟显示。
* UCDOS配合西文软件（比如QBASIC、Telix、MS-DOS Kermit）使用时，UCDOS需要关闭西文制表符识别才能保证所有汉字被正确显示，此时西文制表符绘制的边框会显示成乱码（比如“哪哪哪哪哪”）。

1998s Multimedia PC
-------------------

1998年左右，国内典型的多媒体电脑。

<!--不连网，尽量贴合当年的国情-->

### 配置

* 486 DX2-66MHz CPU
* 8M RAM
* 512M HDD
* S3 Graphics Adapter with 1M VRAM（Windows 3.2下支持640x480高彩色）
* 3.5 Inch Floppy Drive x1
* 5.25 Inch Floppy Drive x1
* CD-ROM
* Sound Blaster 16
* Mouse

### 主要用途

* 文字处理（Word 6.0）
* 电子表格（Excel 5.0）
* 英汉辞典
* 图片浏览
* 听CD、MIDI
* 多媒体光盘浏览
* 小游戏

### 安装说明

DOS下推荐安装以下软件：

* DOS Mario

Windows 3.2的部署（附加组件取舍、声卡驱动）见前文“Windows 3.2部署说明”；本机另不推荐安装“终端仿真程序及其帮助”。

Windows 3.2下如需播放音乐CD，则需安装`[MCI] CD Audio`驱动。

Windows 3.2推荐安装以下软件：

* 金山词霸1.0
* ACDSee
* LView Pro 1.B
* Microsoft Tetris for Windows 2.00
* 五笔字形输入法（绿色安装方案见前文“五笔字形输入法安装说明”）
* Microsoft Office 4.2（详细说明见前文“Microsoft Office 4.2安装说明”）
* 微软乐器大百科
* Microsoft Scenes中的所有JPG图片

### 补充说明

* 制作模拟器使用的BIN+CUE格式的音乐CD镜像可使用`shntool`的`cue`和`join`功能。

