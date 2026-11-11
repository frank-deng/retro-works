Retro Programming Works 怀旧编程作品
====================================

1998s PC
--------

中国90年代后期典型家用多媒体电脑，后期添加网卡高速通天下。

一台想紧跟时代的古董电脑。

<!--硬盘、文件、软件阵容，乱点就乱点，想用啥就用啥，想上啥硬件就上啥硬件，只要符合90年代到千禧年国情-->

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

#### 单机

* 小游戏
* 英汉字典
* 文字处理（Word 6.0）
* 电子表格（Excel 4.2）
* 图片浏览
* 听CD、MIDI
* 多媒体光盘浏览

#### 连网

* 上网看新闻
* 收发邮件
* 连接远端UNIX机器
* FTP上传下载文件

### 安装说明

DOS下推荐安装以下软件：

* SEA（看图软件，支持高彩色、真彩色，可灵活切换分辨率和色深）

Windows 3.2安装时，安装所有附加组件，但以下附件不推荐安装：

* 对象包装程序及其帮助
* 记录器及其帮助
* 录音机及其帮助
* 造字程序及其帮助
* 终端仿真程序及其帮助

Windows 3.2下如需播放音乐CD，则需安装`[MCI] CD Audio`驱动。

Windows 3.2用的Sound Blaster 16驱动推荐安装精简版的，不带播放器和其它工具。

Windows 3.2推荐安装以下软件：

* 五笔字形输入法（绿色安装方案见“五笔字形输入法安装说明”）
* Tetris For Windows
* Microsoft Musical Instruments（多媒体光盘）
* 震撼——古典音乐鉴赏（多媒体光盘）
* ACDSee 2.2 16位版本
* LView Pro 1.B（可用于转换图片格式）
* WinZip（2037年之后不可用）
* Microsoft Office 4.2（需要精选要安装的组件，详细见“Microsoft Office 4.2安装说明”）

Windows 3.2连网场景推荐安装以下软件：

* Trumpet Winsock
* Internet Explorer 3.0（仅安装浏览器）
* Tera Term/SimpTerm/Mocha Telnet/EWAN（通过Telnet连接远端站点）
* WS FTP16LE（FTP客户端）
* FoxMail（邮件客户端）

#### 五笔字形输入法安装说明

五笔字形输入法除了安装相关五笔输入法软件外，还可通过Windows 3.2自带的码表生成器实现。步骤如下：

* 打开码表生成器
* 加载并编译五笔码表文件（`misc/WB.TXT`）
* 在控制面板中的输入法设置中安装“通用码表输入法”即可

#### Microsoft Office 4.2安装说明

Microsoft Office 4.2可选组件非常多，部分组件存在功能冗余、中文乱码、稳定性差、实用价值低等问题，推荐安装的组件如下：

* Word除本体外，只安装“联机帮助、示例”中的“Word帮助”、“示例”
* Excel除本体外，“联机帮助和教程”中只安装“Microsoft Excel帮助”，加载宏中只安装“自动保存”
* Microsoft PowerPoint、Microsoft Office管理器、共享应用程序不安装
* “转换程序、过滤程序和数据存取”中，安装所有文字转换程序和图形过滤程序，“数据存取”不安装
* 工具中只安装“MS Info”
* 可选装长城全真中文字体

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

* Microsoft Word 6.0中可使用EQ域代码写公式，相比使用公式编辑器更可靠，现代Microsoft Word亦支持同款功能。
* Windows 3.2的日历程序建议只用于查看特定年份和月份的日历；卡片盒程序可当备忘录用。
* 制作模拟器使用的BIN+CUE格式的音乐CD镜像可使用`shntool`的`cue`和`join`功能。
* `retro-servers`目录中包含多个自制服务，用于和Windows 3.2中的Internet Explorer 3.0、FoxMail、WS\_FTP、Tera Term等软件对接。
* 该机随时接受任何来自可信外部机器构建的程序，一般通过浏览器或FTP下载。
* Programmer's File Editor在Windows 3.2上无法输入中文，故不予安装。
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


1990s PC开发者版
----------------

1990s PC基础上构建的C、汇编开发机，进行C语言开发的最小配置。配置与1990s PC相同。

### 主要用途

* C语言开发
* 汇编语言开发
* WPS中英文文字处理

### 所用软盘说明

#### MS-DOS 3.3系统软盘

与1990s PC相同。

#### CCDOS软盘

与1990s PC相同。

#### Turbo C 1.0软盘

放入以下文件

	C0S.OBJ
	CS.LIB
	EMU.LIB
	INC/ALLOC.H
	INC/ASSERT.H
	INC/BIOS.H
	INC/CONIO.H
	INC/CTYPE.H
	INC/DIR.H
	INC/DOS.H
	INC/ERRNO.H
	INC/FCNTL.H
	INC/FLOAT.H
	INC/IO.H
	INC/LIMITS.H
	INC/MATH.H
	INC/MEM.H
	INC/PROCESS.H
	INC/SETJMP.H
	INC/SHARE.H
	INC/SIGNAL.H
	INC/STDARG.H
	INC/STDDEF.H
	INC/STDIO.H
	INC/STDLIB.H
	INC/STRING.H
	INC/SYS/STAT.H
	INC/TIME.H
	INC/VALUES.H
	MATHS.LIB
	TCC.EXE
	TLINK.EXE

#### TASM 1.0软盘

待配置


