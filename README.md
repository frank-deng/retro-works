Retro Programming Works ????????
=====================================

Some retro programming works for some old platforms, just for fun.

GW-BASIC
--------

A simple BASIC programming environment, similar to those on home computers in 1980's.

However, due to the [limitations](http://programmingisterrible.com/post/40132515169/dijkstra-basic) of this programming language, only some small programs are available.

Never use it in production environment or for learning purpose.

MS-DOS 5.0 + ANSI.SYS + UCDOS
---

A simple telnet environment with Chinese display and input.

MS-DOS 5.0 + UCDOS + TX.COM
---

An environment use `TX.COM` to display Chinese characters in different sizes and styles.

`TX.COM` is shipped along with UCDOS. Commands for `TX.COM` are generated at server side, then transmitted via a virtual serial line in DOSBox.

Notes 
-----

Convert raw disk image into VDI format image

	VBoxManage convertdd source.img destination.vdi --format VDI

Convert VDI format HDD image into raw one

	VBoxManage clonehd source.vdi destination.img --format RAW
