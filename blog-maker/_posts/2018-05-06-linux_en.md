---
layout: post
title: Linux Skills
tags: [Linux]
---

---

How to deal with Access Denied problem when granting/revoking privileges
------------------------------------------------

1. Shutdown MySQL server.
2. Run MySQL server with command `mysqld_safe --skip-grant-table`.
3. Execute SQL statements for granting/revoking privileges.
4. Kill the `mysqld_safe` process started at step 2.
5. Restart MySQL server.

---

Run program at startup via crontab
----------------------------------

Add the following content to `/etc/crontab`:

	@reboot    username    /path/to/script arguments

---

Keep Laptop Running When Closing Lid
------------------------------------

Edit `/etc/systemd/login.conf` and change the value of `HandleLidSwitch` to `ignore`.

---

Improve Sound Quality for ALSA
------------------------------

Open `/usr/share/alsa/alsa.conf`, then change `defaults.pcm.dmix.rate 48000` into `defaults.pcm.dmix.rate 44100`.

---

Configure autologin for Linux console using `systemd`
-----------------------------------------------------

Firstly, Create directory `/etc/systemd/system/getty@tty1.service.d/` if not exist.

Then create file `/etc/systemd/system/getty@tty1.service.d/autologin.conf` with the following content:

	[Service]
	ExecStart=
	ExecStart=-/sbin/agetty --autologin username --noclear %I $TERM

Then save and reboot.

---

Change Date/Time/Timezone Under Linux
-------------------------------------

Change date: `date -s MM/DD/YYYY`
	
Change time: `date -s hh:mm:ss`

Change timezone: `sudo dpkg-reconfigure tzdata`

---

Record System Output Sound In Linux
-----------------------------------

When pulseaudio is used as the sound server of the system, there is a simple way to record the output sound to file on the command line using `pacat` command.

### Step 1: Find out the correct device

In order to find the correct device, you should run this command:

	pacmd list | grep "\.monitor"
	
When you see something like this:

		name: <alsa_output.pci-0000_00_1b.0.analog-stereo.monitor>
		alsa_output.pci-0000_00_1b.0.analog-stereo.monitor/#0: Monitor of Built-in Audio Analog Stereo
		
and the soundcard corresponds to the one you want to monitor, you can find out which device name to use. Here it is:

	alsa_output.pci-0000_00_1b.0.analog-stereo.monitor

### Step 2: Start recording system output sound

Here are examples of how to record system output sound to a `.wav` file with CD audio quality.

Command using `sox`:

	pacat --record -d alsa_output.pci-0000_00_1b.0.analog-stereo.monitor | sox -t raw -r 44100 -s -L -b 16 -c 2 - output.wav
	
Command using `ffmpeg`:
	
	pacat --record -d alsa_output.pci-0000_00_1b.0.analog-stereo.monitor | ffmpeg -f s16le -ar 44.1k -ac 2 -i pipe:0 record.wav

---

Wifi Configuration Under Linux Console
--------------------------------------

### Preparation

Use `ifconfig -a` to show all the network interfaces available.

### Solution 1 (Connect to one AP only)

Add the following configuration to `/etc/network/interfaces`:

	auto wlan0
	iface wlan0 inet dhcp
		wpa-ssid "WLAN_SSID"
		wpa-psk "12345678"

`wlan0` should be replaced with the Wifi device in use.

### Solution 2 (Connect to different APs based on signal strength)

**Step 1:** Create `/etc/network/wpa_supplicant.conf` with following configuration:

	network={
		ssid="WLAN_AP_1"
		key_mgmt=WPA-PSK
		psk="WLAN_AP_PSK_1"
		priority=1
	}
	network={
		ssid="WLAN_AP_2"
		key_mgmt=WPA-PSK
		psk="WLAN_AP_PSK_2"
		priority=2
	}

**Step 2:** Add the following configuration to `/etc/network/interfaces`

	auto wlan0
	iface wlan0 inet dhcp
		wpa-conf /etc/network/wpa_supplicant.conf

`wlan0` should be replaced with the Wifi device in use.

---

Install Jekyll under Termux
---------------------------

	apt update && apt install libffi-dev clang ruby ruby-dev make
	gem install jekyll

---

Connect To Bluetooth Earphone Via Command Line
----------------------------------------------

1. Install softwares required: `sudo apt-get install bluez bluez-tools rfkill pulseaudio pulseaudio-module-bluetooth pavucontrol`.
2. Restart computer, then use `bluetoothctl` command to enter bluez console.
3. Switch bluetooth earphone into pairing mode to make it discoverable, the use `scan on` command to search for bluetooth devices.
4. Use `devices` command to find out the address of the bluetooth earphone.
5. Use `pair 00:00:00:00:00:00` command to pair the bluetooth earphone. Replace `00:00:00:00:00:00` with the approprate bluetooth address of the bluetooth earphone.
6. Use `connect 00:00:00:00:00:00` command to connect the bluetooth earphone. Replace `00:00:00:00:00:00` with the approprate bluetooth address of the bluetooth earphone.
7. Use `pavucontrol` command to open Pulseaudio control panel, then change the output device to the bluetooth earphone.
8. If you always failed to connect to bluetooth earphones, try to use `pactl load-module module-bluetooth-discover` command to reload PulseAudio's bluetooth module.

---

Mount/unmount MTP devices via command line
------------------------------------------

Mount MTP: `jmtpfs /mnt`

Unmount MTP: `fusermount -u /mnt`

