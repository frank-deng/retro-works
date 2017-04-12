Retro Programming Works 怀旧编程作品
====================================

Some retro programming works for some old platforms, just for fun.

GW-BASIC
--------

A BASIC environment similar to those on home computers in 1980's.

However, due to the [limitations](http://programmingisterrible.com/post/40132515169/dijkstra-basic) of this programming language, the code for this language is very hard to maintain. So only some smaller programs are available.

telnet-site
-----------

A simple site designed for console-based browser [w3m](http://w3m.sourceforge.net), and this site works like an old-school telnet BBS site.

### Server

Website: Nginx + PHP + MySQL

Console: `telnetd.py` + w3m

Configuration:

1. Install package `ncurses-terms`
2. Add `zh_CN.GB2312` to `/etc/locale.gen`, then run `sudo locale-gen`.
3. Set environment variables like below in `.bashrc`:

	TERM=ansi43m
	LANG=zh_CN.GB2312
	LC_ALL=zh_CN.GB2312
	LINES=25
	COLUMNS=80
	WWW_HOME='http://127.0.0.1'

4. Use `w3m -no-mouse` to run `w3m`.
5. Do the following settings in w3m:

* Run external viewer in the background : No
* Use combining characters : No
* Use double width for some Unicode characters : Yes
* Charset conversion when loading : Yes

6. Add the following configuration to `.w3m/keymap`

	keymap	!	NULL
	keymap	#	NULL
	keymap	V	NULL
	keymap	@	NULL
	keymap	|	NULL
	keymap	ESC-w	NULL
	keymap	ESC-W	NULL
	keymap	o	NULL
	keymap	m	NULL
	keymap	r	NULL
	keymap	C-k	NULL
	keymap	D	NULL
	keymap	ESC-c	NULL
	keymap	ESC-o	NULL
	keymap	ESC-k	NULL
	keymap	Q	NULL
	keymap	v	NULL
	keymap	ESC-s	NULL
	keymap	S	NULL
	keymap	E	NULL
	keymap	ESC-e	NULL

### Client

Emulated hardware

* Old 386 platform
* VGA display
* Floppy disk drive only, no hdd available
* Virtual serial modem with Hayes command set

Software

* MS-DOS 5.0
* ANSI.SYS
* UCDOS 7.0
* NRDTERM.EXE

TX-fun
------

An environment use `TX.COM` shipped along with UCDOS to display Chinese characters in different sizes and styles.

Some applications is available for this environment, including applications displaying status of FlightGear, managing calculation programs for *Bulls and Cows* and *2048 Game*.

### Server

	txserver.py
	\-txlogin.py
	  |-txfgfs.py
	  |-txguessnum.py
	  \-tx2048.py

Use the following command to enable serial login for `/dev/ttyS0`:

	systemctl start getty@ttyS0.service
	systemctl enable serial-getty@ttyS0.service
	systemctl status serial-getty@ttyS0.service

### Client

Emulated hardware

* Old 386 platform
* Hercules Monochrome display
* Floppy disk drive only, no hdd available
* Virtual serial line connection

Software

* MS-DOS 5.0
* UCDOS 7.0
* TX.COM
* COMTOOL.COM

Notes 
-----

Convert raw disk image into VDI format image

	VBoxManage convertdd source.img destination.vdi --format VDI

Convert VDI format HDD image into raw one

	VBoxManage clonehd source.vdi destination.img --format RAW

