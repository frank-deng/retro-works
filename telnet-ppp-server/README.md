PPP服务器和Telnet服务器
======================

IE3浏览器可通过PPP协议访问部署在服务端的HTML站点，并配有类似Jekyll的静态博客网站生成器。  
IE3 browser can access the HTML site deployed at server side via PPP protocol. A Jekyll-like static blog site generator is also available.

Telnet服务器可使用类似Telix、HyperTerminal的终端仿真程序通过拨号方式连接。  
Use terminal emulators like Telix, HyperTerminal to dial to the Telnet server.

PPP服务器、Telnet服务器和静态博客网站生成器需要在Linux环境（如Debian、Ubuntu）中运行。  
PPP server, Telnet server and static blog site generator require running under Linux environments like Debian, Ubuntu.

**严禁将PPP服务器或Telnet服务器部署到生产环境或含有敏感数据的环境！！！**  
**DO NOT deploy PPP server or Telnet server to production environment or environment with sensitive data!!!**

### Linux PPP服务器和Telnet服务器配置 Linux PPP Server Configuration

执行以下命令安装所需软件：  
Execute the following commands to install softwares required:

	sudo apt-get install python3 ppp nginx-light php-fpm php-mbstring php-apcu
	cd telnet-ppp-server
	sudo python3 setup.py install

在`/etc/crontab`中加入以下命令，实现开机时自动启动PPP服务器和Telnet服务器：  
Add the following command to `/etc/crontab`, so as to start PPP server on boot:

	@reboot root /usr/local/bin/pppd.py -P 2333 multilink enable-session defaultroute ipcp-accept-remote mtu 576 10.0.2.15: noauth
	@reboot user /usr/local/bin/telnetd.py -P 2345 -c path/to/telnetd.conf

其中`10.0.2.15`是主机或目标站点的IP。  
`10.0.2.15` is the IP address of the host machine or the target site.

对于VIM用户，需要在`/etc/vim/vimrc`中添加以下配置以保证全角双引号和制表符能在终端中正常显示：  
For VIM users, it's necessary to add the following configuration to `/etc/vim/vimrc` for properly displaying fullwidth quote marks and line drawing characters in terminal:

	set ambiwidth=double

### DOSBox串口配置 Configure DOSBox's Serial Interface

在`dosbox-x.conf`所在目录中添加`phonebook.txt`，内容如下：  
Create `phonebook.txt` at the same directory of `dosbox-x.conf`:

	12345 127.0.0.1:2333
	16666 127.0.0.1:2345

将DOSBox配置中`[serial]`小节下的配置项做如下修改：  
Change DOSBox configuration under seciton `[serial]`:

	serial1 = modem
	phonebookfile = phonebook.txt

### VirtualBox NAT配置端口转发 Configure NAT Port Forwarding for VirtualBox

如果PPP服务器和Telnet服务器是部署在VirtualBox虚拟机里的Linux系统上，且虚拟机网卡连接的是NAT网络，则需要在虚拟机网卡的端口转发设置中为虚拟机里的PPP服务器和Telnet服务器分别添加2条端口转发规则，以使得主机上的DOSBox-X能访问虚拟机里的服务。  
If PPP server and Telnet server are deployed on the VirtualBox Linux guest, and guest network adapter is attacted to NAT. Then you must add port forwarding rules for PPP server and Telnet server inside guest machine, so as to enable host DOSBox-x accessing them.

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
PPP服务器和Telnet服务器在虚拟机中使用的端口  
Port numbers of PPP server and Telnet server inside virtual machine.

虚拟机里的程序可以通过`虚拟路由器IP`+`主机上的服务对应的端口号`来访问主机上的服务。虚拟路由器IP可通过以下步骤获得：  
Programs inside virtual machine can access host services via `Virtual Router IP` + `port of the host service`. You can get the virtual router IP via the following steps:

1. 在虚拟机的Linux终端中输入`ip route show`命令。  
Execute command `ip route show` in the guest Linux terminal.
2. 在上一步的命令输出中找到`default via`后面的IP地址，该地址即为客户机的虚拟路由器IP，VirtualBox客户机中一般为`10.0.2.2`。  
Find out the IP address after `default via` from the output of the step above, this is the virtual router IP for the guest machine. For VirtualBox guests it's `10.0.2.2` in most cases.

### Windows 3.x客户端使用方法 Windows 3.x Client Usage

设置新的PPP连接时需要将电话号码设置成`12345`，IP地址设置成`192.168.7.2`，用户名和密码为空。  
When setting up new PPP connection, set phone number with `12345`, set IP address with `192.168.7.2`, leave username and password blank.

如果您有多部虚拟机连接相同的PPP服务器，则需要在每部虚拟机内的系统中分别配置不同的IP地址。比如配置Windows 3.2的IP地址为`192.168.7.2`，Windows 95的IP地址为`192.168.7.3`。  
If you have multiple virtual machines connecting to the same PPP server, then you have to set different IP addresses for each virtual machine. For example, set Windows 3.2's IP address as `192.168.7.2`, and set Windows 95's IP addresss as `192.168.7.3`.

检查“使用远程网上的默认网关”选项是否被选中，否则将无法连接目标服务器。  
Check whether "Use default gateway on remote network" box is checked, or you'll be unable to connect to the target server.

当连接成功时，打开浏览器，使用URL`http://目标站点IP`访问目标站点。  
When connection established, open browser and use URL `http://Target IP` to access the target site.

### 配置博客生成器 Configure Blog Maker

执行以下命令安装所需的软件：  
Execute the following commands to install the softwares required:

	sudo apt-get install nodejs imagemagick

然后进入`blog-maker`目录运行`npm install`安装所需的NodeJS包。  
Then enter `blog-maker` directory and run `npm install` to install NodeJS packages required.

之后运行`npm start`即可生成博客站点内容，生成结果在`dist`目录中。  
After that, run `npm start` to generate the blog site, generated files can be found at `dist` directory.

