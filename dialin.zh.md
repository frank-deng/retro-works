终端拨号连接服务器配置
======================

终端拨号连接服务器可使用类似Telix、HyperTerminal的终端仿真程序通过拨号方式连接。

终端拨号连接服务器需要在Linux环境（如Debian、Ubuntu）中运行，且需事先安装`socat`。

**严禁将终端拨号连接服务器部署到生产环境或含有敏感数据的环境！！！**

部署
----

### Debian/Ubuntu/OpenEuler

安装`socat`后，新建`/usr/local/bin/dialin_login.sh`并设置权限为`500`或`700`，内容如下：

	#!/bin/bash
	TERM='ansi.sys'
	TTY=$(tty)
	TTY=${TTY#/dev/}
	while true; do
		setsid /sbin/agetty --noclear $TTY 57600 $TERM || sleep 1;
	done

在`/etc/crontab`中加入以下命令，实现开机自启动：

	@reboot root socat TCP-LISTEN:23,reuseaddr,fork EXEC:'sh /usr/local/bin/dialin_login.sh',pty,raw,echo=0 &

执行以下命令配置`firewalld`开放所需端口：

	sudo firewall-cmd --add-port=23/tcp --permanent
	sudo firewall-cmd --reload

### Alpine Linux

安装`socat`后，新建`/usr/local/bin/dialin_login.sh`并设置权限为`500`或`700`，内容如下：

	#!/bin/sh
	TERM='ansi'
	TTY=$(tty)
	while true; do
		setsid /sbin/getty 57600 $TTY $TERM || sleep 1;
	done

新建`/etc/init.d/dialin-service`，内容如下：

	#!/sbin/openrc-run
	name="Dial-In Service"
	command="/usr/bin/socat"
	command_args="TCP-LISTEN:23,reuseaddr,fork EXEC:'sh /usr/local/bin/dialin_login.sh',pty,raw,echo=0"
	pidfile="/run/dialin-service.pid"
	command_background=true
	depend() {
	        need net
	}

配置开机自启动：

	rc-update add dialin-service default

虚拟机NAT网络配置端口转发
-------------------------

如果虚拟机网卡连接的是NAT网络，则需要为虚拟机添加端口转发规则，以使得主机上的应用能访问虚拟机里的服务。

* 协议选TCP。
* 主机端口可任意指定一个主机上未使用的端口，连接此端口可访问虚拟机里的服务。
* 子系统端口为拨号连接服务器在虚拟机中使用的端口，一般为23。

DOSBox串口配置
--------------

在`phonebook.txt`中添加以下条目：

	12333 127.0.0.1:2333

将DOSBox配置中`[serial]`小节下的配置项做如下修改：

	serial1 = modem
	phonebookfile = phonebook.txt

文件传输
--------

Debian、Ubuntu、Alpine Linux安装`ckermit`包后可通过Kermit协议互传数据。

OpenEuler需要编译安装`ckermit`。

### 限制

`screen`拉起的shell中不可使用`ckermit`。

GNU Screen
----------

[GNU Screen](https://www.gnu.org/software/screen/)可实现多终端窗口管理，以及将服务端UTF-8编码转换为古董电脑客户端使用的GBK、Shift-JIS编码的功能。

### 推荐配置

在`~/.screenrc`中加入以下配置：

	startup_message off
	cjkwidth on
	vbell off
	shell /bin/bash
	encoding UTF-8 GBK
	bind r source ~/.screenrc

字符编码转换功能在使用`screen -R`重新连接已有GNU Screen会话后会失效，需要重启GNU Screen或重新连接后按`Ctrl-A r`恢复字符编码转换功能。

对于VIM用户，需要在`/etc/vim/vimrc`中添加以下配置以保证全角双引号和制表符能在终端中正常显示：

	set ambiwidth=double

`.bashrc`中推荐添加以下内容，用于显示`screen`会话信息。

	if [[ -n $STY ]]; then
		STYTEXT="[$STY]"
	fi
	PS1="[$?]$STYTEXT \W\n\\$ "

启用Linux的串口终端（可选）
--------------------------

TinyCore Linux中可以在`/opt/bootlocal.sh`中加入以下命令启用串口登录：

	while true; do /sbin/getty 115200 ttyS0; done &

