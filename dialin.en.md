Dial-In Terminal Connection Server
==================================

Use terminal emulators like Telix, HyperTerminal to dial to the dial-up terminal connection server.

Dial-in terminal connection server requires Linux environments like Debian, Ubuntu, and `socat` must be installed first.

**Deploying dial-in terminal connection server to production environment or environment with sensitive data is FORBIDDEN!!!**

Deployment
----------

### Debian/Ubuntu/OpenEuler

After installing `socat`, create `/usr/local/bin/dialin_login.sh` and set the permission as `500` or `700`, file content is as following:

	#!/bin/bash
	TERM='ansi.sys'
	TTY=$(tty)
	TTY=${TTY#/dev/}
	while true; do
		setsid /sbin/agetty --noclear $TTY 57600 $TERM || sleep 1;
	done

Add the following command to `/etc/crontab` to start on boot:

	@reboot root socat TCP-LISTEN:23,reuseaddr,fork EXEC:'sh /usr/local/bin/dialin_login.sh',pty,raw,echo=0 &

Use the following command to configure `firewalld` opening the port required:

	sudo firewall-cmd --add-port=23/tcp --permanent
	sudo firewall-cmd --reload

### Alpine Linux

After installing `socat`, create `/usr/local/bin/dialin_login.sh` and set the permission as `500` or `700`, file content is as following:

	#!/bin/sh
	TERM='ansi'
	TTY=$(tty)
	while true; do
		setsid /sbin/getty 57600 $TTY $TERM || sleep 1;
	done

Create `/etc/init.d/dialin-service` with the follwing content:

	#!/sbin/openrc-run
	name="Dial-In Service"
	command="/usr/bin/socat"
	command_args="TCP-LISTEN:23,reuseaddr,fork EXEC:'sh /usr/local/bin/dialin_login.sh',pty,raw,echo=0"
	pidfile="/run/dialin-service.pid"
	command_background=true
	depend() {
	        need net
	}

Starting service on boot:

	rc-update add dialin-service default

Configure NAT Port Forwarding for VMs
-------------------------------------

If the guest VM's network adapter is attacted to NAT. You must add port forwarding rules for the guest VM，so as to enable host apps accessing services inside guest VM.

* Select TCP protocol.
* Use any unused port as the Host Port, connecting to this port to access the services inside VM.
* Set Guest Port with the port used by the Dial-in server inside VM, usually 23.

Configure DOSBox's Serial Interface
-----------------------------------

Add the following item to `phonebook.txt`:

	12333 127.0.0.1:2333

Change DOSBox configuration under seciton `[serial]`:

	serial1 = modem
	phonebookfile = phonebook.txt

File Transmission
-----------------

Debian、Ubuntu、Alpine Linux安装`ckermit`包后可通过Kermit协议互传数据。  
For Debian, Ubuntu, install `ckermit` package to transmit files via Xmodem/Ymodem/Zmodem protocol.

OpenEuler need compile `ckermit` from source.

### Limitations

Shell launched by `screen` cannot use `ckermit`.

GNU Screen
----------

[GNU Screen](https://www.gnu.org/software/screen/) is used for managing multiple terminal windows, as well as converting server-side's UTF-8 encoding into GBK, Shift-JIS encoding used by clients on vintage computers.

### Recommended Configuration

Add the following configuration to `~/.screenrc`:

	startup_message off
	cjkwidth on
	vbell off
	shell /bin/bash
	encoding UTF-8 GBK
	bind r source ~/.screenrc

Encoding conversion won't work after reattaching to existing GNU Screen session via `screen -R`. Restarting GNU Screen or press `Ctrl-A r` to get encoding conversion work again.

For VIM users, it's necessary to add the following configuration to `/etc/vim/vimrc` for properly displaying fullwidth quote marks and line drawing characters in terminal:

	set ambiwidth=double

Recommended `.bashrc` snippet for displaying `screen` session info.

	if [[ -n $STY ]]; then
		STYTEXT="[$STY]"
	fi
	PS1="[$?]$STYTEXT \W\n\\$ "

## Enable serial console under Linux (Optional)

TinyCore Linux中可以在`/opt/bootlocal.sh`中加入以下命令启用串口登录：  
To enable serial login for TinyCore Linux, add the following command to `/opt/bootlocal.sh`:

	while true; do /sbin/getty 115200 ttyS0; done &

