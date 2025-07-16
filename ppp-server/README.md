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

	tce-load -wi pppd iptables dnsmasq python3.9 expat2

在`/opt/bootlocal.sh`中添加以下命令：  
Add the following command to `/opt/bootlocal.sh`:

	cd /home/tc && python3 ppp-manager.py -c ppp-manager.ini &
	while ! ifconfig|grep $IP_ADDR; do sleep 1; done && /usr/local/sbin/dnsmasq -C /home/tc/dnsmasq.conf &

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

将DOSBox配置中`[serial]`小节下的配置项做如下修改：  
Change DOSBox configuration under seciton `[serial]`:

	serial1 = modem
	phonebookfile = phonebook.txt

## Windows 3.x/95客户端使用方法 Windows 3.x/95 Client Usage

设置新的PPP连接的电话号码为`12345`，IP地址设置成自动获取，用户名和密码为空。  
Add new PPP connection with phone number `12345`, set IP address as automatically fetched, leave username and password blank.

检查“使用远程网上的默认网关”选项是否被选中，否则将无法连接目标服务器。  
Check whether "Use default gateway on remote network" box is checked, or you'll be unable to connect to the target server.

设置DNS地址为`10.0.2.15`。  
Set DNS address as `10.0.2.15`.

检查“拨号后出现终端窗口”选项是否被选中，否则将无法登录。  
Check whether "Bring up terminal window after dialing" box is checked, or you'll be unable to login.

当连接成功时，打开浏览器，使用URL`http://目标站点IP`访问目标站点。  
When connection established, open browser and use URL `http://Target IP` to access the target site.

`ip route show`命令的输出中`default via`后面的IP地址是客户机的虚拟路由器IP，一般为`10.0.2.2`。因此当PPP服务器在虚拟机中运行时，可使用URL`http://10.0.2.2`访问主机上部署的站点。  
Check the output of `ip route show` command, the IP after `default via` is the virtual router IP for the guest machine, normally `10.0.2.2`. So when PPP service is deployed inside VM, use URL `http://10.0.2.2` to access the site on the host machine.

