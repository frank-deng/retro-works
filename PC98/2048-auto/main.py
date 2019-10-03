#!/usr/bin/env python3

import time, ctypes;
lib2048 = ctypes.CDLL('./lib2048.so');
lib2048.find_best_move.argtypes = [ctypes.c_uint64];

def __trailingZeros(num):
    if (num == 0):
        return 0;
    n, result = num, 0;
    while not (n & 1):
        n >>= 1;
        result += 1;
    return result;

def findBestMove(board):
    boardHex = 0;
    i = 0;
    for row in range(4):
        for col in range(4):
            n = __trailingZeros(board[row*4+col]);
            boardHex |= (int(n) << (i*4));
            i += 1;
    return {
        '0': 'UP',
        '1': 'DOWN',
        '2': 'LEFT',
        '3': 'RIGHT',
    }.get(str(lib2048.find_best_move(boardHex)));

TEST=False;
if __name__ == '__main__':
    from Grabber2048 import Grabber2048;
    from pykeyboard import PyKeyboard;
    offline = False;
    kbd = PyKeyboard();
    keyOper = {
        'UP':kbd.up_key,
        'DOWN':kbd.down_key,
        'LEFT':kbd.left_key,
        'RIGHT':kbd.right_key,
    }

    grabber2048 = Grabber2048();
    if(TEST):
        time.sleep(5);
        grabber2048.testTemplate(3, 1, '8');
        exit(0);

    if None != grabber2048.getBoard():
        offline = True;
        timeout = 3;
        print('Please switch to game window in %s seconds'%timeout);
        time.sleep(timeout);
    try:
        while True:
            board = grabber2048.getBoard();
            if None == board:
                if not offline:
                    print('2048 is offline.');
                offline = True;
                continue;
            elif offline:
                print('2048 is online.');
            offline = False;

            move = findBestMove(board);
            if None == move:
                print('Game Over');
                break;
            kbd.tap_key(keyOper[move]);
            time.sleep(0.2);
    except KeyboardInterrupt:
        pass;
    exit(0);

