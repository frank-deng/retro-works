#!/usr/bin/env python3

import os
from setuptools import setup

setup(
    name = 'telnet-ppp-server', # 在pip中显示的项目名称
    version = '0.1',
    author = 'Frank',
    author_email = '',
    licence = 'MIT',
    url = '',
    description = 'PPP server and Telnet server for old platforms like Windows 3.x, Windows 95.',
    python_requires = '>=3.5.0',
    py_modules=['serverLib'],
    scripts=['pppd.py','telnetd.py']
);

