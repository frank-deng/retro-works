#!/bin/bash
MACHINE=$1
echo -n $MACHINE > $HOME/.machine
cd $HOME/$MACHINE
fvwm-root wallpaper.png

