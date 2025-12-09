Retro Programming Works 怀旧编程作品
====================================

1995s PC
--------

多媒体互联网全能电脑，串口互联互通。

### 配置 Configuration

* Pentium 75 CPU
* 8M RAM
* 512M HDD
* S3 Graphics Adapter with 1M VRAM
* 3.5 Inch Floppy Drive x1
* CD-ROM
* Sound Blaster 16
* Mouse
* 56k Modem

### 主要用途 Main Usage

* BASIC编程
* 英汉字典
* 文字处理
* 电子表格
* 图片浏览
* 拨号上网
* 拨号连接远程服务器

### 软件阵容

DOS下推荐安装以下软件：

* SEA（看图软件，支持高彩色、真彩色，可灵活切换分辨率和色深）
* UCDOS 98b+宋体简、仿宋简、黑体简、楷体简轮廓字库
* TELIX（通过串口连接远程服务器，可配合UCDOS实现中文显示和输入）
* The SemWare Editor（程序员使用）

Windows 3.2安装时，以下组件不推荐安装：

* 所有游戏（纸牌、扫雷）
* Windows教程
* 对象包装程序及其帮助
* 记录器及其帮助
* 录音机及其帮助
* 造字程序及其帮助

Windows 3.2声卡驱动不推荐安装任何附加组件，包括播放器、录音机、CD唱机等。

Windows 3.2不建议安装`[MCI] CD Audio`驱动，除非有光盘需要播放CD音轨。

Windows 3.2下推荐安装以下软件：

* Internet Explorer 3.0（包括PPP拨号软件、浏览器、邮件客户端）
* ACDSee 2.2 16位版本
* Microsoft Office 4.2（需要精选要安装的组件，详细见“Microsoft Office 4.2安装说明”）
* 长城全真中文字体
* LView Pro（简单图片处理，可添加文字）
* 五笔字形输入法
* WinZip
* Programmer's File Editor（程序员使用）

#### Microsoft Office 4.2安装说明

Microsoft Office 4.2可选组件非常多，部分组件存在功能冗余、中文乱码、实用价值低等问题，推荐安装的组件如下：

* Word只安装本体和“联机帮助、示例”中的“Word帮助”、“示例”
* Excel除本体外，“联机帮助和教程”中只安装“Microsoft Excel帮助”，加载宏中只安装“自动保存”
* Microsoft PowerPoint和Microsoft Office管理器不安装
* 共享应用程序只安装Media Player
* “转换程序、过滤程序和数据存取”中，安装所有文字转换程序和图形过滤程序，“数据存取”不安装
* 工具中只安装“MS Info”

### 补充说明

* 为保证可维护性，DOS自带的QBASIC建议将代码规模控制在600行以内，用DEBUG的a命令输入QBASIC程序配套的汇编例程时，建议将指令数控制在200条以内。
* QBASIC调用汇编代码的场景，TASM格式的汇编代码可以用DOS自带的`debug`工具的`a`命令输入，此时涉及跳转地址的地方需要手工计算相关地址。


1990s PC
--------

用中文写文章的最小配置。

### 配置

* CPU: 8088 4.77MHz
* RAM: 640k
* Floppy Drive A: 5.25" 360k Double Side
* Floppy Drive B: 5.25" 360k Double Side
* Display: CGA with green monochrome monitor

### 主要用途

* BASIC编程
* WPS中英文文字处理
* 俄罗斯方块游戏
* 2048游戏

### 所用软盘说明

#### MS-DOS 3.3系统软盘

使用`FORMAT B: /S /8 /V`命令制作320k系统引导盘。

系统盘中推荐放入以下文件：

	ATTRIB.EXE
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

#### CCDOS软盘

存放CCDOS汉字系统的基本程序和字库文件。

依次输入`CHLIB`、`VDKEY`命令启动CCDOS汉字系统。

#### WPS软盘

存放WPS、拼音输入法、五笔字形输入法、CCDOS退出程序。

输入`PY`、`WBX`命令加载拼音/五笔字形输入法。

输入`QUIT`命令退出CCDOS。

#### 数据盘

存放所有BASIC程序文件及其依赖数据、WPS文档，以及俄罗斯方块游戏`TETRIS.COM`。

常驻B驱动器。

### 补充说明

* 对于640k RAM的机器，同时加载CCDOS、拼音输入法、五笔字形输入法后，用WPS编辑文章时，单个文件大小控制在2.4k左右，超过此大小容易死机。
* GW-BASIC限制较多，不支持结构化编程，只能使用行号，所有变量皆全局变量，开发前需仔细评估程序复杂度以决定是否移植到GW-BASIC上，开发时需严格控制`GOTO`的使用。

