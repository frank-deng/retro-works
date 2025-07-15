#!/bin/sh

IP_ADDR='10.0.2.15'

while ! ifconfig|grep $IP_ADDR; do
	sleep 1
done
/usr/local/sbin/dnsmasq -C /home/tc/dnsmasq.conf
