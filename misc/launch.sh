#!/bin/bash
sleep $1
PID_FILE=$HOME/dosbox-x.pid
if [[ -f $PID_FILE ]]; then
	exit 1
fi

MACHINE='oldpc'
if [[ -f $HOME/.machine ]]; then
	MACHINE=$(cat $HOME/.machine)
fi
cd $HOME/$MACHINE
dosbox-x -nomenu -conf dosbox-x.conf &>/dev/null & PID=$!
echo $PID > $PID_FILE
wait $PID
rm $PID_FILE
xdotool mousemove 1366 768 &

