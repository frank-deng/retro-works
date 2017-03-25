fun-ucdos
=========

Just for fun.

Notes
-----

### Install DOS from floppy images via DOSBox

	imgmount -t hdd c /path/to/hdd.img -size 512,63,16,X -fs fat
	boot /path/to/disk1.img /path/to/disk2.img /path/to/disk3.img

### Mount HDD image and Floppy for normal use

	imgmount -t floppy 0 /path/to/floppy.img -fs none
	imgmount -t hdd 2 /path/to/hdd.img -size 512,63,16,X -fs none
	boot -l c

