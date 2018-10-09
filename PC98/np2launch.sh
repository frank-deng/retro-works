#!/bin/bash

xrandr --output LVDS-1-1 --mode 1024x576
feh -F black.png &>/dev/null &
PID=$!
xnp2kai &>/dev/null &
PID_NP2=$!
wmctrl -r Neko -e 0,192,87,-1,-1
wait $PID_NP2
kill -2 $PID
xrandr --output LVDS-1-1 --mode 1366x768

