#!/bin/bash
PID_FILE=$HOME/dosbox-x.pid
if [[ -f $PID_FILE ]]; then
	exit 0
fi

MACHINE=$1
echo -n $MACHINE > $HOME/.machine
cd $HOME/$MACHINE
fvwm-root wallpaper.png

