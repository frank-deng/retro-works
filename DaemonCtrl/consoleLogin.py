#!/usr/bin/env python3

from LoginManager import LoginManager;

if __name__ == '__main__':
    loginManager = LoginManager(
        config = {
            'user01': {
                'password': 'aad415a73c4cef1ef94a5c00b2642b571a3e5494536328ad960db61889bd9368',
                'exec': ['bash'],
                'env': {
                    'TERM' : 'ansi43m',
                    'LINES' : '24',
                    'COLUMNS' : '80',
                },
            },
        },
        encoding='GB2312',
        timeout=60
    );
    loginManager.run();
    exit(0);

