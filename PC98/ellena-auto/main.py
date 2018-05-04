#!/usr/bin/env python3

from BLEllena import BLEllena;
import time;

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


def printMoves(move):
    labelMoves = ('Up', 'Left', 'Right', 'Down', 'Middle');
    print(labelMoves[move]);

from pykeyboard import PyKeyboard;
def performMove(move):
    k = PyKeyboard();
    try:
        keyOper = (k.up_key, k.left_key, k.right_key, k.down_key, k.space);
        k.press_key(keyOper[move]);
        time.sleep(0.3);
        k.release_key(keyOper[move]);
    except KeyError:
        print('Unknown move: %s'%move);

ellena = BLEllena();
try:
    lastMove = None;
    lastStatus = None;
    moves = [];
    timestamp = time.time();
    while True:
        status = ellena.getStatus();
        if (None != status and status != lastStatus):
            lastStatus = status;
            if BLEllena.ELLENA_WATCHING == status:
                print('\nWatching:');
                timestamp = time.time();
                moves = [];
            elif BLEllena.ELLENA_ACTIVE == status:
                print('Operating...');
                timestamp = time.time();

        if (BLEllena.ELLENA_WATCHING == status):
            move = ellena.getMove();
            if (None != move and lastMove != move):
                printMoves(move);
                lastMove = move;
                moves.append({
                    'ts': time.time() - timestamp,
                    'mv': move,
                });
        elif (BLEllena.ELLENA_ACTIVE == status):
            lastMove = [];
            if (len(moves) > 0 and time.time() - timestamp >= moves[0]['ts']):
                performMove(moves[0]['mv']);
                moves.pop(0);
        time.sleep(1/30);
except KeyboardInterrupt:
    pass;

