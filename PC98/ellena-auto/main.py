#!/usr/bin/env python3

from BLEllena import BLEllena;
import cv2, time;

def writePpm(fname, pixbuf):
    with open(fname, 'wb') as f:
        f.write(b'P6\n');
        f.write(b'%d %d\n'%(pixbuf.get_width(), pixbuf.get_height()));
        f.write(b'%d\n'%((1 << pixbuf.get_bits_per_sample()) - 1));
        f.write(pixbuf.get_pixels());

def showImage(img, matchedPos = None, tempImg = None):
    WINDOW_TITLE = 'Broadway Legend Ellena';
    if (matchedPos != None and tempImg != None):
        markImg = img.copy();
        for i, pos in enumerate(matchedPos):
            top_left = pos;
            w, h = tempImg[i].shape[:2];
            bottom_right = (top_left[0] + h, top_left[1] + w);
            cv2.rectangle(markImg, top_left, bottom_right, (0, 0, 255), 2);
        cv2.imshow(WINDOW_TITLE, markImg);
    else:
        cv2.imshow(WINDOW_TITLE, img);
    while True:
        k = cv2.waitKey(100);
        if (cv2.getWindowProperty(WINDOW_TITLE, cv2.WND_PROP_VISIBLE) < 1 or k >= 0):
            break;
    cv2.destroyAllWindows();

from pykeyboard import PyKeyboard;
def performMove(move):
    k = PyKeyboard();
    keyOper = (k.up_key, k.left_key, k.right_key, k.down_key, k.space);

    k.press_key(keyOper[move]);
    counter = 100;
    while counter:
        actualMove = ellena.getPlayerMove();
        if(actualMove is None):
            break;
        if (moves[0]['mv'] == actualMove):
            time.sleep(0.01);
            break;
        time.sleep(0);
        counter -= 1;
    k.release_key(keyOper[move]);
    if (counter == 0):
        if (None == actualMove):
            actualMoveStr = 'None';
        else:
            actualMoveStr = labelMoves[actualMove];
        print("Warning: Expected %s, got %s."%(labelMoves[moves[0]['mv']], actualMoveStr));

running = True;
ellena = BLEllena();
labelMoves = ('Up', 'Left', 'Right', 'Down', 'Middle');
try:
    lastMove = None;
    lastStatus = None;
    moves = [];
    timestamp = time.time();
    while running:
        status = ellena.getStatus();
        if (None != status and status != lastStatus):
            lastStatus = status;
            if BLEllena.ELLENA_WATCHING == status:
                timestamp = time.time();
                moves = [];
                lastMove = None;
                print('\nWatching...');
            elif BLEllena.ELLENA_ACTIVE == status:
                timestamp = time.time();
                print('\nOperating...');
            elif BLEllena.ELLENA_FAILED == status:
                running = False;

        if (BLEllena.ELLENA_WATCHING == status):
            move = ellena.getMove();
            if (None != move and lastMove != move):
                moves.append({
                    'ts': time.time() - timestamp,
                    'mv': move,
                    'idx': len(moves),
                });
                print(labelMoves[move]);
            if (None != move):
                lastMove = move;
        elif (BLEllena.ELLENA_ACTIVE == status):
            if (len(moves) > 0):
                performMove(moves[0]['mv']);
                moves.pop(0);
        elif (BLEllena.ELLENA_FAILED == status):
            if (len(moves) > 0):
                print('Failed at move %d (%s, %f)'%(moves[0]['idx'], labelMoves[moves[0]['mv']], moves[0]['ts']));
        time.sleep(0);
except KeyboardInterrupt:
    pass;

