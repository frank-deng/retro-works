#!/usr/bin/env python3
#encoding=UTF-8

from distutils.core import setup
setup(
    name='TX-fun',
    version='0.2',
    author = "frank-deng",
    description = "",
    license = "MIT",
    keywords = "dos ucdos",
    url = "https://github.com/frank-deng/retro-works",  

    platforms = ['Linux'],
    package_dir = {'TX-fun':'.'},
    py_modules = ['TX', 'getch', 'kbhit', 'DaemonCtrl'],
    scripts = ['txserver.py', 'txlogin.py', 'tx2048.py', 'txguessnum.py', 'txfgfs.py']
);

