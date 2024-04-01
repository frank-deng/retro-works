Telnet服务器
============

Telnet服务器可使用类似Telix、HyperTerminal的终端仿真程序通过拨号方式连接。  
Use terminal emulators like Telix, HyperTerminal to dial to the Telnet server.

Telnet服务器需要在Linux环境（如Debian、Ubuntu）中运行。  
Telnet server require running under Linux environments like Debian, Ubuntu.

**严禁将Telnet服务器部署到生产环境或含有敏感数据的环境！！！**  
**DO NOT deploy Telnet server to production environment or environment with sensitive data!!!**

## Telnet服务器配置 Telnet Server Configuration

执行以下命令安装所需软件：  
Execute the following commands to install softwares required:

	sudo apt-get install python3
	sudo pip3 install paramiko

在`/etc/crontab`中加入以下命令，实现开机时自动启动Telnet服务器：  
Add the following command to `/etc/crontab` to start the Telnet server on boot:

	@reboot user python3 /path/to/telnet-ssh-adapter.py -P 2333 -c path/to/ssh.conf

执行以下命令配置`firewalld`开放所需端口：  
Use the following command to configure `firewalld` opening the port required:

    sudo firewall-cmd --add-port=2333/tcp --permanent

## VirtualBox NAT配置端口转发 Configure NAT Port Forwarding for VirtualBox

如果Telnet服务器是部署在VirtualBox虚拟机里的Linux系统上，且虚拟机网卡连接的是NAT网络，则需要在虚拟机网卡的端口转发设置中为虚拟机里的Telnet服务器添加端口转发规则，以使得主机上的DOSBox-X能访问虚拟机里的服务。  
If Telnet server are deployed on the VirtualBox Linux guest, and guest network adapter is attacted to NAT. Then you must add port forwarding rules for the Telnet server inside guest machine, so as to enable host DOSBox-x accessing them.

转发规则各个字段意义如下：  
Meanings of port forwarding rule columns:

* **名称 Name**  
可任意指定，也可以留空。  
Any value is acceptable, including blank value.
* **协议 Protocol**  
此处固定选择`TCP`（此处UDP没有使用）。  
Always select `TCP` here (UDP is unused here).
* **主机IP Host IP**  
可以不指定，也可以指定`127.0.0.1`以限制只有在主机上运行的程序可以访问对应的服务。  
Leave it blank, or specify `127.0.0.1` to limit only programs running on the host machine can access the service.
* **主机端口 Host Port**  
可任意指定一个主机上未使用的端口。  
Any port number not used on the host machine are acceptable.
* **子系统IP Guest IP**  
在虚拟机的Linux里使用`ip address`命令查看虚拟机网卡对应的IP地址，一般是`10.0.2.15`。  
Use command `ip address` inside Linux guest to get the IP address of the guest network card, in most cases it's `10.0.2.15`.
* **子系统端口 Guest Port**  
Telnet服务器在虚拟机中使用的端口  
Port numbers of the Telnet server inside virtual machine.

虚拟机里的程序可以通过`虚拟路由器IP`+`主机上的服务对应的端口号`来访问主机上的服务。虚拟路由器IP可通过以下步骤获得：  
Programs inside virtual machine can access host services via `Virtual Router IP` + `port of the host service`. You can get the virtual router IP via the following steps:

1. 在虚拟机的Linux终端中输入`ip route show`命令。  
Execute command `ip route show` in the guest Linux terminal.
2. 在上一步的命令输出中找到`default via`后面的IP地址，该地址即为客户机的虚拟路由器IP，VirtualBox客户机中一般为`10.0.2.2`。  
Find out the IP address after `default via` from the output of the step above, this is the virtual router IP for the guest machine. For VirtualBox guests it's `10.0.2.2` in most cases.

## DOSBox串口配置 Configure DOSBox's Serial Interface

在`phonebook.txt`中添加以下条目：  
Add the following item to `phonebook.txt`:

	12333 127.0.0.1:2333

将DOSBox配置中`[serial]`小节下的配置项做如下修改：  
Change DOSBox configuration under seciton `[serial]`:

	serial1 = modem
	phonebookfile = phonebook.txt

## GNU Screen

[GNU Screen](https://www.gnu.org/software/screen/)可实现多终端窗口管理，以及将服务端UTF-8编码转换为古董电脑客户端使用的GBK、Shift-JIS编码的功能。
[GNU Screen](https://www.gnu.org/software/screen/) is used for managing multiple terminal windows, as well as converting server-side's UTF-8 encoding into GBK, Shift-JIS encoding used by clients on vintage computers.

### 推荐配置 Recommended Configuration

在`~/.screenrc`中加入以下配置：  
Add the following configuration to `~/.screenrc`:

	defflow off
	deflogin on
	cjkwidth on
	vbell off
	term ansi.sys
	shell /bin/bash
	encoding UTF-8 GBK
	setenv RUN_SCREEN yes

对于VIM用户，需要在`/etc/vim/vimrc`中添加以下配置以保证全角双引号和制表符能在终端中正常显示：  
For VIM users, it's necessary to add the following configuration to `/etc/vim/vimrc` for properly displaying fullwidth quote marks and line drawing characters in terminal:

	set ambiwidth=double

### 已知问题 Known Issues

字符编码转换功能在重新连接已有GNU Screen会话后会失效。需要重启GNU Screen恢复字符编码转换功能。
Encoding conversion won't work after reattaching to existing GNU Screen session. Restarting GNU Screen is needed to get encoding conversion work again.

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

