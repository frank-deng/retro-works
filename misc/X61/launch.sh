#!/bin/bash

cd /home/frank/.oldpc
if [[ -n $1 ]]; then
  sleep $1
fi
#xrandr --output LVDS1 --mode 680x426 --set 'scaling mode' 'Full'
xrandr --output LVDS1 --mode 720x450 --set 'scaling mode' 'Full'
dosbox-x -fs -nomenu -conf dosbox-x.conf &>/dev/null
xrandr --output LVDS1 --mode 1024x768

