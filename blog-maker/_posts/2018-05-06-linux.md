---
layout: post
title: Linux使用技巧
tags: [Linux]
---

---

MySQL如何解决赋予/收回用户权限时发生Access Denied的情况
-------------------------------------------------------

1. 停止MySQL服务。
2. 使用命令`mysqld_safe --skip-grant-table`启动MySQL数据库服务。
3. 进行用户权限的赋予、收回操作。
4. 将第2步启动的`mysqld_safe`进程杀掉。
5. 重启MySQL服务。

---

使用crontab实现开机自动运行脚本
-------------------------------

将以下内容加入到`/etc/crontab`中：

	@reboot    username    /path/to/script arguments

---

防止笔记本合上后进入休眠状态
----------------------------

编辑`/etc/systemd/login.conf`，将`HandleLidSwitch`的值改为`ignore`。

---

提升ALSA播放时的音质
--------------------

打开`/usr/share/alsa/alsa.conf`，然后将`defaults.pcm.dmix.rate 48000`更改为`defaults.pcm.dmix.rate 44100`。

---

为Linux命令行配置自动登录（使用`systemd`）
------------------------------------------

新建目录`/etc/systemd/system/getty@tty1.service.d/`（如果该目录不存在）

然后创建文件`/etc/systemd/system/getty@tty1.service.d/autologin.conf`，文件内容如下：

	[Service]
	ExecStart=
	ExecStart=-/sbin/agetty --autologin username --noclear %I $TERM

保存，然后重启。

---

更改日期、时间、时区
--------------------

更改日期：`date -s MM/DD/YYYY`
	
更改时间：`date -s hh:mm:ss`

更改时区：`sudo dpkg-reconfigure tzdata`

---

Linux命令行下捕获系统声音
-------------------------

当pulseaudio被用于管理系统声音时，可以在命令行环境下使用`pacat`命令捕获系统声音。

### 步骤1：找到用于捕获系统声音的设备

使用以下命令找到用于捕获系统声音的设备：

	pacmd list | grep "\.monitor"
	
当看到如下输出时：

		name: <alsa_output.pci-0000_00_1b.0.analog-stereo.monitor>
		alsa_output.pci-0000_00_1b.0.analog-stereo.monitor/#0: Monitor of Built-in Audio Analog Stereo
		
就可以找到用于捕获系统声音的设备了。在上述输出内容中，可以找到设备名如下：

	alsa_output.pci-0000_00_1b.0.analog-stereo.monitor

### 步骤2：开始捕获系统声音

以下例子描述了如何将系统声音拷贝到`.wav`文件中，并使用CD音质。

使用`sox`的命令:

	pacat --record -d alsa_output.pci-0000_00_1b.0.analog-stereo.monitor | sox -t raw -r 44100 -s -L -b 16 -c 2 - output.wav
	
使用`ffmpeg`的命令:
	
	pacat --record -d alsa_output.pci-0000_00_1b.0.analog-stereo.monitor | ffmpeg -f s16le -ar 44.1k -ac 2 -i pipe:0 record.wav

---

Linux命令行下配置Wifi
---------------------

### 前期准备

使用`ifconfig -a`命令获取所有可用的网络设备。

### 方案1（只需连1个路由器）

将以下配置加入到`/etc/network/interfaces`中：

	auto wlan0
	iface wlan0 inet dhcp
		wpa-ssid "WLAN_SSID"
		wpa-psk "12345678"

其中`wlan0`需要换成需要使用的Wifi设备。

### 方案2（根据信号强度连接不同路由器）

**第1步：**创建`/etc/network/wpa_supplicant.conf`，并添加以下配置：

	network={
		ssid="WLAN_SSID_1"
		key_mgmt=WPA-PSK
		psk="WLAN_AP_PSK_1"
		priority=1
	}
	network={
		ssid="WLAN_SSID_2"
		key_mgmt=WPA-PSK
		psk="WLAN_AP_PSK_2"
		priority=2
	}

**第2步：**将以下配置加入到`/etc/network/interfaces`中：

	auto wlan0
	iface wlan0 inet dhcp
		wpa-conf /etc/network/wpa_supplicant.conf

其中`wlan0`需要换成需要使用的Wifi设备。

---

Termux下安装Jekyll
------------------

	apt update && apt install libffi-dev clang ruby ruby-dev make
	gem install jekyll

---

使用命令行连接蓝牙耳机
----------------------

1. 使用以下命令安装所需软件`sudo apt-get install bluez bluez-tools rfkill pulseaudio pulseaudio-module-bluetooth pavucontrol`。
2. 重启电脑，然后输入命令`bluetoothctl`进入bluez控制台。
3. 将蓝牙耳机调整到配对模式，使之可被搜索到，然后在电脑上使用`scan on`命令搜索设备。
4. 使用`devices`命令找到蓝牙耳机对应的蓝牙地址
5. 使用`pair 00:00:00:00:00:00`命令与蓝牙耳机配对，需要把命令中的`00:00:00:00:00:00`换成蓝牙耳机对应的蓝牙地址。
6. 使用`connect 00:00:00:00:00:00`命令与蓝牙耳机连接，需要把命令中的`00:00:00:00:00:00`换成蓝牙耳机对应的蓝牙地址。
7. 使用`pavucontrol`命令打开Pulseaudio控制台，将输出设备设置成蓝牙耳机即可。
8. 如果连接蓝牙耳机一直失败，可尝试使用`pactl load-module module-bluetooth-discover`命令加载PulseAudio的蓝牙模块以修复问题。

---

使用命令行挂载/卸载MTP设备
--------------------------

挂载MTP：

	jmtpfs /mnt

卸载MTP：

	fusermount -u /mnt

