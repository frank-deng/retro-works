PPP服务器
=========

IE3浏览器可通过PPP协议访问部署在服务端的HTML站点。  
IE3 browser can access the HTML site deployed at server side via PPP protocol.

PPP服务器需要在Linux环境（如Debian、Ubuntu、TinyCore）中运行。  
PPP server requires running under Linux environments like Debian, Ubuntu, TinyCore.

**严禁将PPP服务器部署到生产环境或含有敏感数据的环境！！！**  
**DO NOT deploy PPP server to production environment or environment with sensitive data!!!**

推荐在TinyCore Linux虚拟机上部署。  
TinyCore Linux VM is recommended.

## Tiny Core Linux PPP服务器部署 Deploy PPP Server On Tiny Core Linux

安装所需软件包：  
Install packages required:

	tce-load -wi pppd iptables dnsmasq python3.9 expat2

将以下文件传至PPP服务器上的`/home/tc`目录：  
Transfer the following files to `/home/tc` directory on the PPP server:

	ppp-manager.py
	util.py
	ppp-manager.ini

在`/opt/bootlocal.sh`中添加以下命令：  
Add the following command to `/opt/bootlocal.sh`:

	cd /home/tc && python3 ppp-manager.py -c ppp-manager.ini &

执行`sudo filetool.sh -b`命令保存修改。  
Execute `sudo filetool.sh -b` command to save all the modifications.

## Linux PPP服务器部署 Deploy Linux PPP Server

安装`iptables`、`python3`、`ppp`、`dnsmasq`。  
Install `iptables`, `python3`, `ppp`, `dnsmasq`.

将以下文件传至Linux服务器：  
Transfer the following files to the Linux server:

	ppp-manager.py
	util.py
	ppp-manager.ini

在`/etc/crontab`中加入以下命令，实现开机时自动启动PPP服务器：  
Add the following command to `/etc/crontab`, so as to start PPP server on boot:

	@reboot root cd /path/to/ppp-manager && python3 ppp-manager.py

执行以下命令配置`firewalld`开放所需端口：  
Use the following command to configure `firewalld` opening the port required:

    sudo firewall-cmd --add-port=2345/tcp --permanent

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

检查“拨号后出现终端窗口”选项是否被选中，否则将无法登录。  
Check whether "Bring up terminal window after dialing" box is checked, or you'll be unable to login.

