Some notes on DOSBox
--------------------

在DOSBox中使用软盘安装DOS  
Install DOS from floppy images via DOSBox

	imgmount -t hdd c /path/to/hdd.img -size 512,63,16,X -fs fat
	boot /path/to/disk1.img /path/to/disk2.img /path/to/disk3.img

将原始硬盘镜像转换成VDI格式硬盘镜像  
Convert raw disk image into VDI format image

	VBoxManage convertdd source.img destination.vdi --format VDI

将VDI格式硬盘镜像转换成原始硬盘镜像  
Convert VDI format HDD image into raw one

	VBoxManage clonehd source.vdi destination.img --format RAW

DOSBox中使用硬盘镜像  
Mount raw disk image and floppy image

	imgmount -t floppy 0 /path/to/floppy.img -fs none
	imgmount -t hdd 2 /path/to/hdd.img -size 512,63,16,X -fs none
	boot -l c

一些有用的键盘码  
Some Useful KeyCodes

* `\r`: Enter
* `\x1B`: Esc
* `\x00H`: Up
* `\x00P`: Down
* `\x00K`: Left
* `\x00M`: Right

