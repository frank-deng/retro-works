-----
title: DOS Skills
tags: [DOS]
-----

Add CD-ROM support for MS-DOS
-----------------------------

Copy `OAKCDROM.SYS` to `C:\` (`OAKCDROM.SYS` can be found from Windows 9x installation CD-ROMs).

Copy `MSCDEX.EXE` to `C:\` if MSCDEX is not installed.

Add the following configuration into `CONFIG.SYS`:

	DEVICEHIGH=C:\OAKCDROM.SYS /D:CD1
	LASTDRIVE=Z

Add the following command into `AUTOEXEC.BAT`:

	LH MSCDEX.EXE /D:CD1 /L:Z

`/L:Z` specifies the drive letter for CD-ROM.

Reduce CPU Usage Of Emulator
----------------------------

MS-DOS 6.22 has pre-installed `POWER.EXE`, you can add the following configuration into `CONFIG.SYS`:

	DEVICEHIGH=C:\DOS\POWER.EXE ADV:MAX

For other versions of MS-DOS, copy `IDLE.COM` to `C:\`, then run it from `AUTOEXEC.BAT`. `IDLE.COM` can be found from *Microsoft Virtual PC 2007*.

For Windows 3.x, copy `WQGHLT.386` to `C:\WINDOWS\SYSTEM\`, then open `C:\WINDOWS\SYSTEM.INI` and add the following configuration into `[386enh]` section:

	device=wqghlt.386

Change Text Color For UCDOS WPS
-------------------------------

Default color of UCDOS WPS, green text on blue background is too hard to read. Use `WPS /FE /S` command to change color into yellow text on blue background, which looks more clear.

Use `WPS /?` for command line help info.

How to install S3 video driver for Windows 3.x
----------------------------------------------

Use the basic VGA driver for the initial install, then change the video driver using Windows Setup in the Main program group.

When the driver spouted up a prompt to Insert the Trio 64V Flat Mode Driver disk, redirect the installer to `C:\WINDOWS\SYSTEM\` to complete the graphics driver install.

Use DOSBox-x's printer under Windows 3.x
----------------------------------------

Select `Epson LQ1600K` as the printer driver, then you can print document into PNG files from Windows 3.x applications via DOSBox-x's virtual printer.

DOSBox-x printer paper size recommends width 83 and height 114, which corresponds to A4 size.

DOSBox-X Configuration Skills
-----------------------------

Set configuration `locking disk image mount` with `true` if poasible. So as to prevent disk image corruption due to multiple running instances writing to the same disk image.

Use configuration `hard drive data rate limit` to specify the speed of hard drive and CD-ROM drive. Use configuration `floppy drive data rate limit` to specify the speed of floppy drive (Some earlier version DOSBox-X did not support adjusting floppy drive speed independently).

