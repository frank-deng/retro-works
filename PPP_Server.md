PPP服务器
=========

Windows 3.x/95虚拟机里的浏览器可通过PPP协议访问部署在服务端的HTML站点。  
Windows 3.x/95 VM can access the HTML site deployed at server side via PPP protocol.

PPP服务器需要在Linux环境（如Debian、Ubuntu、TinyCore）中运行。  
PPP server requires running under Linux environments like Debian, Ubuntu, TinyCore.

**！！！严禁将PPP服务器部署到生产环境或含有敏感数据的环境！！！**  
**!!! Deploying PPP server to production environment or environment with sensitive data is FORBIDDEN !!!**

推荐在单独的TinyCore Linux虚拟机上部署PPP服务器。  
Standalone TinyCore Linux VM is recommended for deploying PPP server.

## Tiny Core Linux PPP服务器部署 Deploy PPP Server On Tiny Core Linux

安装所需软件包：  
Install packages required:

	tce-load -wi pppd socat iptables dnsmasq

在PPP服务器上添加以下文件，各文件内容如下：  
Add the following files to PPP server, each file has content below:

### `/etc/ppp/options`

	require-chap
	nodefaultroute
	mtu 576
	proxyarp
	lock
	ms-dns 10.0.2.15
	10.0.2.15:

### `/etc/ppp/chap-secrets`

	ppp	  *  ppp   192.168.7.1
	ppp2  *  ppp2  192.168.7.2

### `/etc/dnsmasq.conf`

	server=8.8.8.8
	listen-address=10.0.2.15
	address=/mysite.com/10.0.2.2
	address=/www.mysite.com/10.0.2.2
	bind-interfaces
	no-resolv
	no-hosts

在`/opt/bootlocal.sh`中添加以下命令：  
Add the following command to `/opt/bootlocal.sh`:

	sysctl -w net.ipv4.ip_forward=1
	iptables -t nat -A POSTROUTING -s 192.168.7.0/24 -j MASQUERADE
	iptables -t nat -A PREROUTING -d 10.0.2.2 -p tcp --dport 80 -j DNAT --to-destination :8080
	iptables -t nat -A OUTPUT -d 10.0.2.2 -p tcp --dport 80 -j REDIRECT --to-port 8080
	while ! ifconfig -a|grep -q "inet addr:10.0.2.15"; do sleep 1; done;
	dnsmasq
	socat TCP-LISTEN:2345,reuseaddr,fork EXEC:'sh -c "/usr/local/sbin/pppd \$(tty)"',pty,stderr,setsid &

在`/opt/.filetool.lst`中添加以下路径：  
Add the following path to `/opt/.filetool.lst`:

	etc/dnsmasq.conf
	etc/ppp
	usr/local/etc/ppp

执行`sudo filetool.sh -b`命令保存修改。  
Execute `sudo filetool.sh -b` command to save all the modifications.

## 虚拟机NAT网络配置端口转发 Configure NAT Port Forwarding for VMs

如果虚拟机网卡连接的是NAT网络，则需要为虚拟机添加端口转发规则，以使得主机上的应用能访问虚拟机里的服务。  
If the guest VM's network adapter is attacted to NAT. Then you must add port forwarding rules for the guest VM，so as to enable host apps accessing services inside guest VM.

* 协议选TCP。  
  Select TCP protocol.
* 主机端口可任意指定一个主机上未使用的端口，连接此端口可访问虚拟机里的服务。  
  Use any unused port as the Host Port, connecting to this port to access the services inside VM.
* 子系统端口为PPP服务器在虚拟机中使用的端口，比如2345。  
  Set Guest Port with the port used by PPP server inside VM, e.g. 2345.

## DOSBox串口配置 Configure DOSBox's Serial Interface

在`phonebook.txt`中添加以下条目：  
Add the following item to `phonebook.txt`:

	12345 127.0.0.1:2345

将DOSBox-X配置中`[serial]`小节下的配置项做如下修改：  
Change DOSBox configuration under seciton `[serial]`:

	serial1 = modem
	phonebookfile = phonebook.txt

## Windows 3.x/95客户端使用方法 Windows 3.x/95 Client Usage

设置新的PPP连接的电话号码为`12345`，IP和DNS地址设置成自动获取，用户名和密码为`ppp/ppp`或`ppp2/ppp2`。  
Add new PPP connection with phone number `12345`, set IP and DNS address as automatically fetched, use `ppp/ppp` or `ppp2/ppp2` for username and password.

Windows 95需要检查“使用远程网上的默认网关”选项是否被选中，否则将无法连接目标服务器。  
For Windows 95, enable "Use default gateway on remote network" first, or you'll be unable to connect to the target server.

**注意：**必须保证所有PPP连接使用单独的用户名，否则将导致PPP服务器异常。
**WARNING: **Username for each PPP connection must be unique, otherwise the PPP server may become abnormal.

