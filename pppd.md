ISP服务器配置
=============

PPP服务器需要在Linux环境（如Debian、Ubuntu、TinyCore）中运行。推荐在单独的TinyCore Linux虚拟机上部署PPP服务器。

**！！！严禁将PPP服务器部署到生产环境或含有敏感数据的环境！！！**

**TinyCore Linux中，任何文件修改后都需要执行`sudo filetool.sh -b`命令保存修改，否则重启后修改会丢失！！！**

TinyCore Linux配置
------------------

安装所需软件包

	tce-load -wi pppd socat iptables dnsmasq

在`/opt/.filetool.lst`中添加以下路径：

	etc/ppp
	usr/local/etc/ppp
	etc/dnsmasq.conf

新建或覆盖`/etc/ppp/options`，内容如下：

	require-chap
	nodefaultroute
	mtu 576
	nodetach
	proxyarp
	lock
	ms-dns 10.0.2.15
	10.0.2.15:

新建或覆盖`/etc/ppp/chap-secrets`，内容如下：

	ppp   *  ppp   192.168.7.1
	ppp2  *  ppp2  192.168.7.2

执行以下命令配置端口转发，TinyCore Linux安装好后只需执行一次：

	# PPP连接专用转发规则
	iptables -t nat -A POSTROUTING -s 192.168.7.0/24 -j MASQUERADE
	
	# 添加其它端口转发规则：80-8080、25-8025、110-8110
	iptables -t nat -A PREROUTING -d 10.0.2.2 -p tcp --dport 80 -j DNAT --to-destination :8080
	iptables -t nat -A OUTPUT -d 10.0.2.2 -p tcp --dport 80 -j REDIRECT --to-port 8080
	iptables -t nat -A PREROUTING -d 10.0.2.2 -p tcp --dport 25 -j DNAT --to-destination :8025
	iptables -t nat -A OUTPUT -d 10.0.2.2 -p tcp --dport 25 -j REDIRECT --to-port 8025
	iptables -t nat -A PREROUTING -d 10.0.2.2 -p tcp --dport 110 -j DNAT --to-destination :8110
	iptables -t nat -A OUTPUT -d 10.0.2.2 -p tcp --dport 25 -j REDIRECT --to-port 8110
	
	# 保存转发规则
	iptables-save > /opt/iptables-rules

新建或覆盖`/etc/dnsmasq.conf`，内容如下：

	bind-interfaces
	no-resolv
	no-hosts
	server=8.8.8.8
	listen-address=10.0.2.15
	address=/mysite.com/10.0.2.2
	address=/www.mysite.com/10.0.2.2

将以下命令添加到`/opt/bootlocal.sh`中：

	sysctl -w net.ipv4.ip_forward=1
	iptables-restore < /opt/iptables-rules
	while ! ifconfig -a|grep -q "inet addr:10.0.2.15"; do sleep 1; done;
	dnsmasq
	socat TCP-LISTEN:2345,reuseaddr,nodelay,fork system:'/usr/local/sbin/pppd "$SOCAT_PTY"',pty,stderr,setsid &

执行`sudo filetool.sh -b`命令保存修改。

### 说明

以上安装步骤中，`10.0.2.15`为网卡IP地址（一般通过DHCP获取到），`10.0.2.2`为虚拟路由器地址，部署时需根据实际情况调整。


虚拟机NAT网络配置端口转发
-------------------------

如果虚拟机网卡连接的是NAT网络，则需要为虚拟机添加端口转发规则，以使得主机上的应用能访问虚拟机里的服务。

* 协议选TCP。
* 主机端口可任意指定一个主机上未使用的端口，连接此端口可访问虚拟机里的服务。
* 子系统端口为PPP服务器在虚拟机中使用的端口，比如2345。


DOSBox串口配置
--------------

在`phonebook.txt`中添加以下条目：

	12345 127.0.0.1:2345

将DOSBox-X配置中`[serial]`小节下的配置项做如下修改：

	serial1 = modem
	phonebookfile = phonebook.txt


Windows 3.x/95客户端使用方法
----------------------------

设置新的PPP连接的电话号码为`12345`，IP和DNS地址设置成自动获取，用户名和密码为`ppp/ppp`或`ppp2/ppp2`。

Windows 95需要检查“使用远程网上的默认网关”选项是否被选中，否则将无法连接目标服务器。

**注意：**必须保证所有PPP连接使用单独的用户名，否则将导致PPP服务器异常。

