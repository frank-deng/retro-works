from WindowGrabber import WindowGrabber;
import numpy as np;
import cv2;

class BLEllena(WindowGrabber):
    ELLENA_WATCHING = 'ELLENA_WATCHING';
    ELLENA_ACTIVE = 'ELLENA_ACTIVE';
    def __init__(self, winTitle = r'Neko Project'):
        npRunning = WindowGrabber.getWindowByTitle(winTitle);
        if (len(npRunning) == 0):
            raise SystemError('No instances of Neko Project II is running.');
        elif (len(npRunning) > 1):
            raise SystemError('More than 1 instances of Neko Project II is running.');
        WindowGrabber.__init__(self, npRunning[0]);

        self.imgLightHorOn = cv2.imread('images/light_h_on.png');
        self.imgLightVerOn = cv2.imread('images/light_v_on.png');
        self.imgEllenaWatching = cv2.imread('images/ellena_watching.png');
        self.imgEllenaActive = cv2.imread('images/ellena_active.png');

    def __capture(self):
        pixbuf = self.capture();
        cvimg = cv2.cvtColor(
            np.fromstring(pixbuf.get_pixels(), np.uint8).reshape(
                pixbuf.get_height(),
                pixbuf.get_width(),
                pixbuf.get_n_channels()
            ),
            cv2.COLOR_BGR2RGB
        );
        return cvimg;

    def __match(self, src, tempImg, threshold):
        res = cv2.matchTemplate(src, tempImg, cv2.TM_CCOEFF_NORMED);
        loc = list(zip(*np.where(res >= threshold)[::-1]));
        return loc;

    def __matchPos(self, posList, target = None):
        if (None == target):
            return len(posList) > 0;
        for pos in posList:
            if (pos[0] == target[0] and pos[1] == target[1]):
                return True;
        return False;

    def getStatus(self):
        cvimg = self.__capture();
        if len(self.__match(cvimg, self.imgEllenaWatching, 0.6)):
            return self.ELLENA_WATCHING;
        elif len(self.__match(cvimg, self.imgEllenaActive, 0.6)):
            return self.ELLENA_ACTIVE;
        return None;

    def getMove(self):
        cvimg = self.__capture();
        lightsHor = self.__match(cvimg, self.imgLightHorOn, 0.6);
        lightsVer = self.__match(cvimg, self.imgLightVerOn, 0.6);
        result = [];
        if (self.__matchPos(lightsHor, (456, 0))):
            result.append(0);
        if (self.__matchPos(lightsVer, (320, 145))):
            result.append(1);
        if (self.__matchPos(lightsVer, (608, 144))):
            result.append(2);
        if (self.__matchPos(lightsHor, (456, 304))):
            result.append(3);

        if (len(result) == 1):
            return result[0];
        elif (len(result) == 4):
            return 4;
        else:
            return None;

