8086机器软件阵容配置说明
========================

MS-DOS 3.3系统软盘
------------------

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

CCDOS软盘
---------

存放CCDOS汉字系统的基本程序和字库文件。

依次输入`CHLIB`、`VDKEY`命令启动CCDOS汉字系统。

WPS软盘
-------

存放WPS、拼音输入法、五笔字形输入法、CCDOS退出程序。

输入`PY`、`WBX`命令加载各输入法。

使用`QUIT`命令退出CCDOS。

数据盘
------

常驻B驱动器，存放所有BASIC程序文件及其依赖数据、WPS文档，以及TETRIS游戏。

