fun-ucdos
=========

Just for fun.

------

?DOSBox???????????DOS  
Install DOS from floppy images via DOSBox

	imgmount -t hdd c /path/to/hdd.img -size 512,63,16,X -fs fat
	boot /path/to/disk1.img /path/to/disk2.img /path/to/disk3.img

??????????VDI???????  
Convert raw disk image into VDI format image

	VBoxManage convertdd source.img destination.vdi --format VDI

?VDI????????????????  
Convert VDI format HDD image into raw one

	VBoxManage clonehd source.vdi destination.img --format RAW

?????????????  
Mount raw disk image and floppy image

	imgmount -t floppy 0 /path/to/floppy.img -fs none
	imgmount -t hdd 2 /path/to/hdd.img -size 512,63,16,X -fs none
	boot -l c

??????  
Some Useful KeyCodes

* `\r`: Enter
* `\x1B`: Esc
* `\x00H`: Up
* `\x00P`: Down
* `\x00K`: Left
* `\x00M`: Right

