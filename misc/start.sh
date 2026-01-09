#!/bin/bash

taskset -c 1 qemu-system-x86_64 \
-pidfile /tmp/alpine-x86_64.pid \
-machine q35 -cpu qemu64 -smp 1 -m 512 \
-accel kvm \
-drive file=$HOME/alpine-x86_64.qcow2,index=0 \
-netdev user,id=network0,hostfwd=tcp:127.0.0.1:2333-:23,dns=8.8.8.8 \
-device virtio-net,netdev=network0 \
-monitor unix:$HOME/alpine-monitor.sock,server=on,wait=off \
-serial unix:$HOME/alpine-serial.sock,server=on,wait=off \
-parallel none -no-reboot -boot d \
-display none -daemonize

taskset -c 1 qemu-system-i386 \
-pidfile $PREFIX/tmp/tinycore.pid \
-machine type=q35,hpet=off -cpu max,vendor=GenuineIntel -smp 1 -m 128 \
-accel kvm \
-netdev user,id=network0,hostfwd=tcp:127.0.0.1:2345-:2345,dns=8.8.8.8 \
-device virtio-net,netdev=network0 \
-drive file=$HOME/tinycore.qcow2,format=qcow2 \
-display none -no-reboot -daemonize -boot d \
-serial unix:$HOME/tinycore-serial.sock,server,nowait

cd $HOME/retro-works/servers && taskset -c 1 python3 server.py &

