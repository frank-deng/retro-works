#!/data/data/com.termux/files/usr/bin/bash
rm telnetd.log mysite.log
python telnetd.py -H 127.0.0.1 -P 2333 -L ./mylogin.py &>> telnetd.log &
python main.py -H 127.0.0.1 &>>mysite.log &