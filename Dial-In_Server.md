终端拨号连接服务器 Dial-In Terminal Connection Server
=====================================================

终端拨号连接服务器可使用类似Telix、HyperTerminal的终端仿真程序通过拨号方式连接。  
Use terminal emulators like Telix, HyperTerminal to dial to the dial-up terminal connection server.

终端拨号连接服务器需要在Linux环境（如Debian、Ubuntu）中运行，且需事先安装`socat`。  
Dial-in terminal connection server requires Linux environments like Debian, Ubuntu, and `socat` must be installed first.

**严禁将终端拨号连接服务器部署到生产环境或含有敏感数据的环境！！！**  
**Deploying dial-in terminal connection server to production environment or environment with sensitive data is FORBIDDEN!!!**

## 部署 Deployment

### Debian/Ubuntu/OpenEuler

安装`socat`后，新建`/usr/local/bin/dialin_login.sh`并设置权限为`500`或`700`，内容如下：  
After installing `socat`, create `/usr/local/bin/dialin_login.sh` and set the permission as `500` or `700`, file content is as following:

	#!/bin/bash
	TERM='ansi.sys'
	TTY=$(tty)
	TTY=${TTY#/dev/}
	while true; do
		setsid /sbin/agetty --noclear $TTY 57600 $TERM || sleep 1;
	done

在`/etc/crontab`中加入以下命令，实现开机自启动：  
Add the following command to `/etc/crontab` to start on boot:

	@reboot root socat TCP-LISTEN:2333,reuseaddr,fork EXEC:'sh /usr/local/bin/dialin_login.sh',pty,raw,echo=0

执行以下命令配置`firewalld`开放所需端口：  
Use the following command to configure `firewalld` opening the port required:

	sudo firewall-cmd --add-port=2333/tcp --permanent

### Alpine Linux

安装`socat`后，新建`/usr/local/bin/dialin_login.sh`并设置权限为`500`或`700`，内容如下：  
After installing `socat`, create `/usr/local/bin/dialin_login.sh` and set the permission as `500` or `700`, file content is as following:

	#!/bin/sh
	TERM='ansi'
	TTY=$(tty)
	while true; do
		setsid /sbin/getty 57600 $TTY $TERM || sleep 1;
	done

新建`/etc/init.d/dialin-service`，内容如下：  
Create `/etc/init.d/dialin-service` with the follwing content:

	#!/sbin/openrc-run
	name="Dial-In Service"
	command="/usr/bin/socat"
	command_args="TCP-LISTEN:2333,reuseaddr,fork EXEC:'sh /usr/local/bin/dialin_login.sh',pty,raw,echo=0"
	pidfile="/run/dialin-service.pid"
	command_background=true
	depend() {
	        need net
	}

配置开机自启动：  
Starting service on boot:

	rc-update add dialin-service default

## 虚拟机NAT网络配置端口转发 Configure NAT Port Forwarding for VMs

如果虚拟机网卡连接的是NAT网络，则需要为虚拟机添加端口转发规则，以使得主机上的应用能访问虚拟机里的服务。  
If the guest VM's network adapter is attacted to NAT. Then you must add port forwarding rules for the guest VM，so as to enable host apps accessing services inside guest VM.

* 协议选TCP。  
  Select TCP protocol.
* 主机端口可任意指定一个主机上未使用的端口，连接此端口可访问虚拟机里的服务。  
  Use any unused port as the Host Port, connecting to this port to access the services inside VM.
* 子系统端口为PPP服务器在虚拟机中使用的端口，比如2345。  
  Set Guest Port with the port used by PPP server inside VM, e.g. 2345.

## 虚拟机访问主机上的服务 Access Services on the Host from VM

`ip route show`命令的输出中`default via`后面的IP地址是客户机的虚拟路由器IP，一般为`10.0.2.2`。虚拟机中的程序可通过`虚拟路由器IP + 端口`连接主机上的服务。  
Check the output of `ip route show` command, the IP after `default via` is the virtual router IP for the guest machine, normally `10.0.2.2`. Programs inside VM can access the services on the host via `Virtual Router IP + Port`.

## DOSBox串口配置 Configure DOSBox's Serial Interface

在`phonebook.txt`中添加以下条目：  
Add the following item to `phonebook.txt`:

	12333 127.0.0.1:2333

将DOSBox配置中`[serial]`小节下的配置项做如下修改：  
Change DOSBox configuration under seciton `[serial]`:

	serial1 = modem
	phonebookfile = phonebook.txt

## 文件传输 File Transmission

Debian、Ubuntu、OpenEuler安装`lrzsz`包后可通过Xmodem/Ymodem/Zmodem协议互传数据。  
For Debian, Ubuntu, OpenEuler, install `lrzsz` package to transmit files via Xmodem/Ymodem/Zmodem protocol.

Alpine Linux需要从源码编译安装lrzsz。  
Alpine Linux need compile lrzsz from source.

## GNU Screen

[GNU Screen](https://www.gnu.org/software/screen/)可实现多终端窗口管理，以及将服务端UTF-8编码转换为古董电脑客户端使用的GBK、Shift-JIS编码的功能。
[GNU Screen](https://www.gnu.org/software/screen/) is used for managing multiple terminal windows, as well as converting server-side's UTF-8 encoding into GBK, Shift-JIS encoding used by clients on vintage computers.

### 推荐配置 Recommended Configuration

在`~/.screenrc`中加入以下配置：  
Add the following configuration to `~/.screenrc`:

	cjkwidth on
	vbell off
	shell /bin/bash
	encoding UTF-8 GBK
	bind r source ~/.screenrc

字符编码转换功能在使用`screen -R`重新连接已有GNU Screen会话后会失效，需要重启GNU Screen或重新连接后按`Ctrl-A r`恢复字符编码转换功能。  
Encoding conversion won't work after reattaching to existing GNU Screen session via `screen -R`. Restarting GNU Screen or press `Ctrl-A r` to get encoding conversion work again.

对于VIM用户，需要在`/etc/vim/vimrc`中添加以下配置以保证全角双引号和制表符能在终端中正常显示：  
For VIM users, it's necessary to add the following configuration to `/etc/vim/vimrc` for properly displaying fullwidth quote marks and line drawing characters in terminal:

	set ambiwidth=double

`.bashrc`中推荐添加以下内容，用于显示`screen`会话信息。  
Recommended `.bashrc` snippet for displaying `screen` session info.

	if [[ -n $STY ]]; then
		STYTEXT="[$STY]"
	fi
	PS1="[$?]$STYTEXT \W\n\\$ "

## 启用Linux的串口终端（可选） Enable serial console under Linux (Optional)

临时为`/dev/ttyS0`启用串口登录（重启后失效）：  
Temporarily enable serial console on `/dev/ttyS0` (Inavailable after reboot):

	systemctl start getty@ttyS0.service

永久为`/dev/ttyS0`启用串口登录：  
Permanently enable serial console on `/dev/ttyS0`:

	systemctl enable serial-getty@ttyS0.service

查看`/dev/ttyS0`的串口登录功能是否启用：  
Check whether serial console is enabled on `/dev/ttyS0`:

	systemctl status serial-getty@ttyS0.service

TinyCore Linux中可以在`/opt/bootlocal.sh`中加入以下命令启用串口登录：  
To enable serial login for TinyCore Linux, add the following command to `/opt/bootlocal.sh`:

	while true; do /sbin/getty 115200 ttyS0; done &

