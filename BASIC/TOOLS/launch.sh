#!/bin/bash

cd /home/frank/oldpc
if [[ -f 'dosbox-x.pid' ]]; then
	exit 1
fi

fvwm-root overlay.png
dosbox-x -nomenu -conf dosbox-x.conf &>/dev/null & PID=$!
echo $PID > dosbox-x.pid
wait $PID
rm dosbox-x.pid
fvwm-root wallpaper.png

