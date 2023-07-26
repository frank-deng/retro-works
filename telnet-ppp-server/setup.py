#!/usr/bin/env python3

import os,sys;
from setuptools import setup;

if 'linux'!=sys.platform:
    print("This package only supports Linux platform.");
    exit(1);

setup(
    name = 'telnet-ppp-server', # 在pip中显示的项目名称
    version = '0.1',
    author = 'Frank',
    author_email = '',
    license = 'MIT',
    url = '',
    description = 'PPP server and Telnet server for old platforms like Windows 3.x, Windows 95.',
    python_requires = '>=3.5.0',
    scripts=['utils.py', 'telnetd.py']
);
