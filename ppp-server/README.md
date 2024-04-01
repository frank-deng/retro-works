PPP服务器
=========

IE3浏览器可通过PPP协议访问部署在服务端的HTML站点。  
IE3 browser can access the HTML site deployed at server side via PPP protocol.

PPP服务器需要在Linux环境（如Debian、Ubuntu、TinyCore）中运行。  
PPP server requires running under Linux environments like Debian, Ubuntu, TinyCore.

**严禁将PPP服务器部署到生产环境或含有敏感数据的环境！！！**  
**DO NOT deploy PPP server to production environment or environment with sensitive data!!!**

## Linux PPP服务器配置 Linux PPP Server Configuration

执行以下命令安装所需软件：  
Execute the following commands to install softwares required:

	sudo apt-get install iptables python3 ppp

开启IP转发：将`/etc/sysctl.conf`中的`net.ipv4.ip_forward`的值改为`1`。  
Enable IP Forwarding: Modify `/etc/sysctl.conf` and change the value of `net.ipv4.ip_forward` into `1`.

在`/etc/crontab`中加入以下命令，实现开机时自动启动PPP服务器：  
Add the following command to `/etc/crontab`, so as to start PPP server on boot:

	@reboot root python3 /path/to/ppp-manager.py -P 2345 -c path/to/ppp.conf
	@reboot root iptables -t nat -A POSTROUTING -s 192.168.7.0/24 -j MASQUERADE

在`/etc/ppp/options`中加入以下配置：  
Add the following configuration to `/etc/ppp/options`:

	lock
	nodetach
	multilink
	enable-session
	defaultroute
	mtu 576
	noauth

执行以下命令配置`firewalld`开放所需端口：  
Use the following command to configure `firewalld` opening the port required:

    sudo firewall-cmd --add-port=2345/tcp --permanent

## Tiny Core Linux PPP服务器配置 Tiny Core Linux PPP Server Configuration

安装所需软件包 Install packages required

	tce-load -wi pppd iptables python3.9

在`/opt/bootlocal.sh`中添加以下命令：  
Add the following command to `/opt/bootlocal.sh`:

	sysctl -w net.ipv4.ip_forward=1
	iptables -t nat -A POSTROUTING -s 192.168.7.0/24 -j MASQUERADE
	python3 /path/to/ppp-manager.py --port 2345 --config path/to/ppp.conf --pppd /path/to/pppd &

执行`backup`命令保存修改。  
Use `backup` command to save all the modifications.

## VirtualBox NAT配置端口转发 Configure NAT Port Forwarding for VirtualBox

如果PPP服务器是部署在VirtualBox虚拟机里的Linux系统上，且虚拟机网卡连接的是NAT网络，则需要在虚拟机网卡的端口转发设置中为虚拟机里的PPP服务器添加端口转发规则，以使得主机上的DOSBox-X能访问虚拟机里的服务。  
If PPP server is deployed in the VirtualBox Linux guest, and guest network adapter is attacted to NAT. Then you must add port forwarding rules for the PPP server inside guest machine, so as to enable host DOSBox-x accessing them.

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
PPP服务器在虚拟机中使用的端口，比如2345  
Port numbers of PPP server inside virtual machine, e.g. 2345.

虚拟机里的程序可以通过`虚拟路由器IP`+`主机上的服务对应的端口号`来访问主机上的服务。虚拟路由器IP可通过以下步骤获得：  
Programs inside virtual machine can access host services via `Virtual Router IP` + `port of the host service`. You can get the virtual router IP via the following steps:

1. 在虚拟机的Linux终端中输入`ip route show`命令。  
Execute command `ip route show` in the guest Linux terminal.
2. 在上一步的命令输出中找到`default via`后面的IP地址，该地址即为客户机的虚拟路由器IP，VirtualBox客户机中一般为`10.0.2.2`。  
Find out the IP address after `default via` from the output of the step above, this is the virtual router IP for the guest machine. For VirtualBox guests it's `10.0.2.2` in most cases.

## DOSBox串口配置 Configure DOSBox's Serial Interface

在`phonebook.txt`中添加以下条目：  
Add the following item to `phonebook.txt`:

	12345 127.0.0.1:2345

将DOSBox配置中`[serial]`小节下的配置项做如下修改：  
Change DOSBox configuration under seciton `[serial]`:

	serial1 = modem
	phonebookfile = phonebook.txt

## Windows 3.x/95客户端使用方法 Windows 3.x/95 Client Usage

设置新的PPP连接的电话号码为`12345`，IP地址设置成自动获取，用户名和密码为空。  
Add new PPP connection with phone number `12345`, set IP address as automatically fetched, leave username and password blank.

检查“使用远程网上的默认网关”选项是否被选中，否则将无法连接目标服务器。  
Check whether "Use default gateway on remote network" box is checked, or you'll be unable to connect to the target server.

检查“拨号后出现终端窗口”选项是否被选中，否则将无法登录。  
Check whether "Bring up terminal window after dialing" box is checked, or you'll be unable to login.

当连接成功时，打开浏览器，使用URL`http://目标站点IP`访问目标站点。  
When connection established, open browser and use URL `http://Target IP` to access the target site.

