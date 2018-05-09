#!/usr/bin/env python3

from LoginManager import LoginManager;

if __name__ == '__main__':
    loginManager = LoginManager(
        config = {
            'user': {
                'password': '04f8996da763b7a969b1028ee3007569eaf3a635486ddab211d512c85b9df8fb',
                'exec': ['w3m', '-no-mouse'],
                'env': {
                    'TERM' : 'ansi43m',
                    'LANG' : 'zh_CN.GB2312',
                    'LC_ALL' : 'zh_CN.GB2312',
                    'LANGUAGE' : 'zh_CN:zh',
                    'LINES' : '24',
                    'COLUMNS' : '80',
                    'WWW_HOME' : 'http://127.0.0.1:8080',
                },
            },
        },
        encoding='GB2312',
        welcome='*** 欢迎光临我的信息港 ***',
        lang={
            'username': '用户名：',
            'password': '密　码：',
            'login_success': '登录成功！',
            'login_failed': '登录失败！',
            'timeout_msg': '%d秒内无用户输入，退出。',
        }
    );
    loginManager.run();
    exit(0);
