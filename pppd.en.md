Configure PPP Internet Access
=============================

Using PPP server, Windows 3.x/95 VM can access the HTML website deployed at server side via PPP protocol.

PPP server requires running under Linux environments like Debian, Ubuntu, TinyCore.

**!!! Deploying PPP server to production environment or environment with sensitive data is FORBIDDEN !!!**

Standalone TinyCore Linux VM is recommended for deploying PPP server.

Deploy PPP Server On Tiny Core Linux
------------------------------------

Install packages required:

	tce-load -wi pppd socat iptables dnsmasq

Create or replace `/etc/ppp/options` with the following content:

	require-chap
	nodefaultroute
	mtu 576
	nodetach
	proxyarp
	lock
	ms-dns 10.0.2.15
	10.0.2.15:

Create or replace `/etc/ppp/chap-secrets` with the following content:

	ppp   *  ppp   192.168.7.1
	ppp2  *  ppp2  192.168.7.2

Create or replace `/etc/dnsmasq.conf` with the following content:

	bind-interfaces
	no-resolv
	no-hosts
	server=8.8.8.8
	listen-address=10.0.2.15
	address=/mysite.com/10.0.2.2
	address=/www.mysite.com/10.0.2.2

Add the following command to `/opt/bootlocal.sh`:

	sysctl -w net.ipv4.ip_forward=1
	iptables -t nat -A POSTROUTING -s 192.168.7.0/24 -j MASQUERADE
	while ! ifconfig -a|grep -q "inet addr:10.0.2.15"; do sleep 1; done;
	dnsmasq
	socat TCP-LISTEN:2345,reuseaddr,fork system:'/usr/local/sbin/pppd "$SOCAT_PTY"',pty,stderr,setsid &

When the host machine cannot use 80 port and use 8080 port instead, use the following command in PPP server to forward `10.0.2.2:80` requests to `10.0.2.2:8080`:

	iptables -t nat -A PREROUTING -d 10.0.2.2 -p tcp --dport 80 -j DNAT --to-destination :8080
	iptables -t nat -A OUTPUT -d 10.0.2.2 -p tcp --dport 80 -j REDIRECT --to-port 8080

Add the following path to `/opt/.filetool.lst`:

	etc/dnsmasq.conf
	etc/ppp
	usr/local/etc/ppp

Execute `sudo filetool.sh -b` command to save all the modifications.

Configure NAT Port Forwarding for VMs
-------------------------------------

If the guest VM's network adapter is attacted to NAT. Then you must add port forwarding rules for the guest VM，so as to enable host apps accessing services inside guest VM.

* Select TCP protocol.
* Use any unused port as the Host Port, connecting to this port to access the services inside VM.
* Set Guest Port with the port used by PPP server inside VM, e.g. 2345.

Configure DOSBox's Serial Interface
-----------------------------------

Add the following item to `phonebook.txt`:

	12345 127.0.0.1:2345

Change DOSBox configuration under seciton `[serial]`:

	serial1 = modem
	phonebookfile = phonebook.txt

Windows 3.x/95 Client Usage
---------------------------

Add new PPP connection with phone number `12345`, set IP and DNS address as automatically fetched, use `ppp/ppp` or `ppp2/ppp2` for username and password.

For Windows 95, enable "Use default gateway on remote network" first, or you'll be unable to connect to the target server.

**WARNING: **Username for each PPP connection must be unique, otherwise the PPP server may become abnormal.

