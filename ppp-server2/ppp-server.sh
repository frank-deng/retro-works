#!/bin/sh

IP_ADDR='10.0.2.15'
sysctl -w net.ipv4.ip_forward=1
iptables -t nat -A POSTROUTING -s 192.168.7.0/24 -j MASQUERADE
iptables -t nat -A PREROUTING -p tcp --dport 80 -j DNAT --to-destination :8080
iptables -t nat -A OUTPUT -d 0.0.0.0 -p tcp --dport 80 -j REDIRECT --to-port 8080
while ! ifconfig -a|grep -q "inet addr:${IP_ADDR}"; do sleep 1; done;
dnsmasq "--listen-address=${IP_ADDR}"
socat TCP-LISTEN:2345,reuseaddr,fork EXEC:'sh -c "/usr/local/sbin/pppd \$(tty)"',pty,stderr,setsid &

