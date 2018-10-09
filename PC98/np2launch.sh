#!/bin/bash

xrandr --output LVDS-1-1 --mode 1024x576
PID="";
if [[ -f /usr/local/share/icons/black.png ]]; then
	feh -F /usr/local/share/icons/black.png &>/dev/null &
	PID=$!
else
	feh -F black.png &>/dev/null &
	PID=$!
fi
xnp2kai &>/dev/null &
PID_NP2=$!
sleep 0.5
wmctrl -a Neko
wmctrl -r Neko -e 0,192,0,-1,-1
wait $PID_NP2;

xrandr --output LVDS-1-1 --mode 1366x768
kill -2 $PID

