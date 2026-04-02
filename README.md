Retro Programming Works 怀旧编程作品
====================================

1998s PC
--------

家用多媒体互联网电脑，大憨憨和小憨憨共用。

### 配置

* 486 DX2-66MHz CPU
* 8M RAM
* 512M HDD
* S3 Graphics Adapter with 1M VRAM（Windows 3.2下支持640x480高彩色）
* 3.5 Inch Floppy Drive x1
* CD-ROM
* Sound Blaster 16
* Mouse
* 56k Modem

### 主要用途

| 用途             | 大憨憨 | 小憨憨 |
|:-----------------|:------:|:------:|
| BASIC编程        |        | Y      |
| 小游戏           |        | Y      |
| 英汉字典         | Y      | Y      |
| 文字处理         | Y      | Y      |
| 电子表格         | Y      | Y      |
| 图片浏览         | Y      | Y      |
| 听CD、MIDI       |        | Y      |
| 多媒体光盘浏览   |        | Y      |
| 上网看新闻       | Y      | 受监督 |
| 收发邮件         | Y      | 受监督 |

### 安装说明

DOS下推荐安装以下软件：

* UCDOS 98b+宋体简、仿宋简、黑体简、楷体简轮廓字库
* SEA（看图软件，支持高彩色、真彩色，可灵活切换分辨率和色深）

Windows 3.2安装时，安装所有附加组件，但以下附件不推荐安装：

* 对象包装程序及其帮助
* 记录器及其帮助
* 录音机及其帮助
* 造字程序及其帮助

Windows 3.2下如需播放音乐CD，则需安装`[MCI] CD Audio`驱动。

Windows 3.2用的Sound Blaster 16驱动推荐安装精简版的，不带播放器和其它工具。

Windows 3.2推荐安装以下软件：

* Microsoft Office 4.2（需要精选要安装的组件，详细见“Microsoft Office 4.2安装说明”）
* 长城全真中文字体
* ACDSee 2.2 16位版本
* WinZip
* LView Pro（简单图片处理，可添加文字）
* 五笔字形输入法（绿色安装方案见“五笔字形输入法安装说明”）
* Tetris For Windows
* Microsoft Scenes中的所有JPG图片
* Microsoft Musical Instruments（多媒体光盘）
* 震撼——古典音乐鉴赏（多媒体光盘）
* Internet Explorer 3.0（包括PPP拨号软件、浏览器、邮件客户端）

#### Microsoft Office 4.2安装说明

Microsoft Office 4.2可选组件非常多，部分组件存在功能冗余、中文乱码、稳定性差、实用价值低等问题，推荐安装的组件如下：

* Word除本体外，只安装“联机帮助、示例”中的“Word帮助”、“示例”
* Excel除本体外，“联机帮助和教程”中只安装“Microsoft Excel帮助”，加载宏中只安装“自动保存”
* Microsoft PowerPoint、Microsoft Office管理器、共享应用程序不安装
* “转换程序、过滤程序和数据存取”中，安装所有文字转换程序和图形过滤程序，“数据存取”不安装
* 工具中只安装“MS Info”

#### 五笔字形输入法安装说明

五笔字形输入法除了安装相关五笔输入法软件外，还可通过Windows 3.2自带的码表生成器实现。

**安装**：打开码表生成器，加载并编译五笔码表文件（`misc/WB.TXT`），然后在控制面板中的输入法设置中安装“通用码表输入法”即可。

**注意**：码表总条目数不能超过**16384**个，超过部分无法打出。默认五笔码表文件`misc/WB.TXT`仅提供单字支持，常用词语需自行添加。

### 补充说明

* 为保证可维护性，DOS自带的QBASIC建议将代码规模控制在600行以内，用DEBUG的a命令输入QBASIC程序配套的汇编例程时，建议将指令数控制在200条以内。
* QBASIC调用汇编代码的场景，TASM格式的汇编代码可以用DOS自带的`debug`工具的`a`命令输入，此时涉及跳转地址的地方需要手工计算相关地址。
* Microsoft Word 6.0中可使用EQ域代码写公式，相比使用公式编辑器更可靠，现代Microsoft Word亦支持同款功能。
* UCDOS WPS默认的蓝底绿字难以看清，可用`WPS /FE /S`命令改为更清楚的蓝底黄字。用`WPS /?`获取命令行帮助信息。
* UCDOS配合西文软件（比如QBasic、MS-DOS Kermit）使用时，UCDOS需要关闭西文制表符识别才能保证所有汉字被正确显示，此时西文制表符绘制的边框会显示成乱码（比如“哪哪哪哪哪”）。
* Windows 3.2的日历程序建议只用于查看特定年份和月份的日历；卡片盒程序可当备忘录用；终端仿真程序可用于排查Modem相关问题。
* 制作模拟器使用的BIN+CUE格式的音乐CD镜像可使用`shntool`的`cue`和`join`功能。


1990s PC
--------

用中文写文章的最小配置，汉字在信息时代浴火重生之纪念。

### 配置

* CPU: 8088 4.77MHz
* RAM: 640k
* Floppy Drive A: 5.25" 360k Double Side
* Floppy Drive B: 5.25" 360k Double Side
* Display: CGA with green monochrome monitor

### 主要用途

* WPS中英文文字处理
* BASIC编程
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
* GW-BASIC限制较多，不支持结构化编程，只能使用行号，所有变量皆全局变量，开发前需仔细评估程序复杂度以决定是否移植到GW-BASIC上，开发时需严格控制`GOTO`的使用以保证一定程度的可维护性。


1999s GEEK Laptop
-----------------

极客神本，曾经的壕本。串口通天下，远程工作使用。

### 配置

* 486 DX-33MHz CPU
* 8M RAM
* 512M HDD
* S3 Graphics Adapter with 512k VRAM（Windows 3.2下支持640x480 256色）
* External 3.5 Inch Floppy Drive x1
* TouchPad as mouse
* PCMCIA 56k Modem work as COM1
* 640x480 TFT Screen

### 主要用途

* 拨号上网
* 连接远端UNIX机器（TEK4010绘图指令支持）

### 486端安装说明

DOS下推荐安装以下软件：

* UCDOS 98b（不安装任何附加字库）
* MS-DOS Kermit（拨号连接远程终端，使用Kermit协议上传、下载文件）

MS-DOS Kermit需要在主程序所在目录放上本仓`misc`目录下的`MSKERMIT.INI`，以保证其正常工作。

Windows 3.2安装时，推荐安装方案如下：

* 安装所有自述文件，除打印机自述文件外
* 游戏、屏幕保护程序、壁纸等杂项不安装
* 附件只安装以下组件及其对应帮助文件：终端仿真程序、画笔、记事本、计算器、字符映射表
* `AUTOEXEC.BAT`结尾可添加`WIN`命令，以实现开机时直接进入Windows 3.x。

Windows 3.2推荐安装以下软件：

* Internet Explorer 3.0（包括PPP拨号软件、浏览器、邮件客户端）
* Tera Term/SimpTerm/Mocha Telnet/EWAN（通过TELNET连接远端站点）
* WS FTP16LE（FTP客户端）
* 五笔字形输入法（绿色安装方案见前文“五笔字形输入法安装说明”）
* WinZip

### Linux端安装说明

* 可使用tcpser实现虚拟modem
* 需要部署PPP服务器和telnet服务器
* 电子表格可使用`sc-im`+`gnuplot`实现
* FTP服务端可使用`vsftpd`

### 补充说明

* Windows 3.2适合多任务并发处理，但不适合处理高负载任务。高负载任务（比如TEK图形绘制）需退出Windows 3.2，在纯DOS模式中处理。
* DOSBox-X模拟器存在Bug，只能使用一个串口。86Box使用`hlt`指令不能降低主机负载。
* Windows 3.2的终端仿真程序可用于排查Modem、自制ISP（PPP服务器）相关问题。
* 不建议使用Windows 3.2 Tera Term的TEK绘图功能，极易导致系统卡死。建议使用DOS下的MS-DOS Kermit的TEK绘图功能。
* TEK40xx绘图功能，基准分辨率为1024x780，Y轴方向为从下往上，与一般屏幕Y轴方向相反。
* Programmer's File Editor在Windows 3.2上无法输入中文，故不予安装。
* 不建议用于对速度、稳定性要求高的任务，此类任务请使用现代系统。

