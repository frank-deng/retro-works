Retro Programming Works 怀旧编程作品
====================================

被模拟的PC 1 Emulated PC 1
------------------------

### 年代 Era

* 1995 ~ 1998

### 配置 Configuration

* CPU 80486DX4-100
* 16M RAM
* 1G HDD
* S3 Graphics Adapter with 1M VRAM
* 3.5 Inch Floppy Drive x1
* CD-ROM
* Sound Blaster 16
* Mouse
* 56k Modem

### 主要用途 Main Usage

* BASIC编程 BASIC Programming
* C/C++编程 C/C++ Programming
* 英汉字典 English-Chinese dictionary
* 中英文文字处理 Chinese & English text processing
* 电子表格和图表处理 Spreadsheet and chart processing
* 图片浏览 Image viewing
* 音乐和视频播放 Music & video playback
* 拨号上网 Surfing online via dial-up network
* 拨号连接远程服务器 Connecting to remote server via dial-up network
* （禁止游戏 NO GAMING）

被模拟的PC 2 Emulated PC 2
-------------------------

### 年代 Era

* 1990 ~ 1992

### 配置 Configuration

* CPU: 8088 4.77MHz
* RAM: 640k
* Floppy Drive A: 5.25" 360k Double Side
* Floppy Drive B: 5.25" 360k Double Side
* Display: CGA with green monochrome monitor

### 主要用途 Main Usage

* BASIC编程 BASIC Programming
* WPS中英文文字处理 WPS Chinese & English Text Processing
* 俄罗斯方块游戏 Tetris game
* 2048游戏 2048 Game


实用命令 Useful Commands
------------------------

### 制作VCD并在Windows 95下播放

使用ffmpeg制作VCD  
Convert video into VCD

	ffmpeg -i input.mp4 -target pal-vcd|ntsc-vcd output.mpg
	vcdimager -t vcd2 -l "Movie Title" -c output.cue -b output.bin output.mpg

使用ffmpeg制作VCD并将源视频分成多长碟片（每张碟片最长1小时）  
Convert video into VCD and split the source video into multiple discs (Maximum 1 hour for each disc)

	ffmpeg -ss 00:00:00 -t 00:60:00 -i input.mp4 -target pal-vcd|ntsc-vcd output1.mpg
	vcdimager -t vcd2 -l "Part 1" -c output1.cue -b output1.bin output1.mpg
	ffmpeg -ss 00:60:00 -t 00:30:00 -i input.mp4 -target pal-vcd|ntsc-vcd output2.mpg
	vcdimager -t vcd2 -l "Part 2" -c output2.cue -b output2.bin output2.mpg

Windows 95使用**金山影霸II**播放PAL制式VCD，使用XingMPEG Player播放NTSC制式VCD。  
Under Windows 3.2 and Windows 95, use SoftVCD II (JinShanYinBa II) to play PAL VCD, use XingMPEG Player to play NTSC VCD.

### 其它 Miscellaneous

Linux下挂载虚拟软盘（使用GB2312编码的文件名）  
Mount floppy image under Linux (Use GB2312 for filename encoding)

	sudo mount -o loop,codepage=936,iocharset=utf8 floppy.img /mnt

对于一些BIN/CUE，MDF/MDS等非ISO格式的光盘映像文件，可以尝试在Linux下使用`iat`命令转换成ISO文件  
For CD-ROM image files in non-ISO format like BIN/CUE, MDF/MDS, etc., try to use `iat` command under Linux to convert them into ISO file.

