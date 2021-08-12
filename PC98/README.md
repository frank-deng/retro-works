Retro Programming Works for NEC PC-9800 Series
==============================================

Some retro programming works for NEC PC-9800 Series.

Use Turbo C++ 4.0J to compile all the C programs (Disable memory managers like `EMM386.EXE` and only keep `HIMEM.SYS` in `CONFIG.SYS` before running Turbo C++ 4.0J).

2048 For PC-98
--------------

Gabriele Cirulli's 2048 game for NEC PC-9800 Series.

### Screenshots

![2048](https://frank-deng.github.io/retro-works/PC98/screenshots/2048_1.png)

![2048](https://frank-deng.github.io/retro-works/PC98/screenshots/2048_2.png)

![2048](https://frank-deng.github.io/retro-works/PC98/screenshots/2048_3.png)


Countdown Timer
---------------

A simple countdown timer for NEC PC-9800 Series, using beep speaker for alarming.

### Screenshots

![Countdown Timer](https://frank-deng.github.io/retro-works/PC98/screenshots/timer1.png)

![Countdown Timer](https://frank-deng.github.io/retro-works/PC98/screenshots/timer2.png)


Sudoku Solver
-------------

### Screenshots

![Sudoku Solver](https://frank-deng.github.io/retro-works/PC98/screenshots/sudoku.png)


*Strong in the Rain* by Kenji Miyazawa
------------------------------------

![雨ニモマケズ](https://frank-deng.github.io/retro-works/PC98/screenshots/poem1.png)


Add CD-ROM support
------------------

Add the following configuration to `CONFIG.SYS`:

	DEVICEHIGH=A:¥DOS¥NECCDD.SYS /D:CD1
	LASTDRIVE=Z

Add the following command to `AUTOEXEC.BAT`:

	MSCDEX.EXE /D:CD1 /L:Z

`/L:Z` specifies the drive letter for CD-ROM.

Make PC98 Background Image in 16/256 color
------------------------------------------

1. On the host machine, use image processors like GIMP to create a BMP file in 640x400 resolution, indexed 16/256 color mode.  
When exporting BMP file using GIMP, always expand **Compatibility Options** and check **Do not write color space information** option when "Export as BMP" dialog pops up, or exported BMP file will be incompatible with most of the softwares.
2. Copy the saved BMP file to PC98, then run `mg .BMP.MAG export.bmp` at PC98 emulator side to convert `.BMP` file to `.MAG` file (in MAKI-chan image format).  
`mg` can be downloaded from [here](https://www.vector.co.jp/soft/dos/art/se002524.html), `EMM386.EXE` must be loaded in `CONFIG.SYS` before running it.
3. Use `mag256 export.mag` command to display `.MAG` image file on the graphic layer beneath text.  
`MAG256.COM` can be downloaded from [here](https://www.vector.co.jp/soft/dos/art/se050872.html), `MOUSE.COM` must be loaded first or system crash will happen when running it.

