from WindowGrabber import WindowGrabber;
import cv2;
import numpy as np;

class Grabber2048(WindowGrabber):
    def __init__(self, templatePath = 'numbers.png', winTitle = r'Neko Project'):
        WindowGrabber.__init__(self, winTitle);

        template = cv2.imread(templatePath);
        self.__numberTemplate = {
            '0':      template[0:16,0:40],
            '2':      template[1*16:2*16,0:40],
            '4':      template[2*16:3*16,0:40],
            '8':      template[3*16:4*16,0:40],
            '16':     template[4*16:5*16,0:40],
            '32':     template[5*16:6*16,0:40],
            '64':     template[6*16:7*16,0:40],
            '128':    template[7*16:8*16,0:40],
            '256':    template[8*16:9*16,0:40],
            '512':    template[9*16:10*16,0:40],
            '1024':   template[10*16:11*16,0:40],
            '2048':   template[11*16:12*16,0:40],
            '4096':   template[12*16:13*16,0:40],
            '8192':   template[13*16:14*16,0:40],
            '16384':  template[14*16:15*16,0:40],
            '32768':  template[15*16:16*16,0:40],
            '65536':  template[16*16:17*16,0:40],
        };

    def __capture(self):
        pixbuf = self.capture();
        if(None==pixbuf):
            return None;
        cvimg = cv2.cvtColor(
            np.fromstring(pixbuf.get_pixels(), np.uint8).reshape(
                pixbuf.get_height(),
                pixbuf.get_width(),
                pixbuf.get_n_channels()
            ),
            cv2.COLOR_BGR2RGB
        );
        return cvimg;

    def __matchTemplateExact(self,img0,img1):
        w, h = img0.shape[1], img0.shape[0];
        x = y = 0;
        while y < h:
            while x < w:
                r0, g0, b0 = img0[y, x, 0], img0[y, x, 1], img0[y, x, 2];
                r1, g1, b1 = img1[y, x, 0], img1[y, x, 1], img1[y, x, 2];
                v0 = 0;
                if (r0 or g0 or b0):
                    v0 = 1;
                v1 = 0;
                if (r1 or g1 or b1):
                    v1 = 1;
                if (v0 != v1):
                    return False;
                x += 1;
            x, y = 0, y+1;
        return True;

    def __getNum(self, src):
        for n in self.__numberTemplate:
            dest = self.__numberTemplate[n];
            if (self.__matchTemplateExact(src,dest)):
                return int(n);
        return None;

    def __processImg(self, image):
        w, h = image.shape[1], image.shape[0];
        x = y = 0;
        while y < h:
            while x < w:
                r = image[y, x, 0];
                g = image[y, x, 1];
                b = image[y, x, 2];
                if (r > 1 and r < 254) or (g > 1 and g < 254) or (b > 1 and b < 254):
                    image[y, x, 0] = 0;
                    image[y, x, 1] = 0;
                    image[y, x, 2] = 0;
                x += 1;
            x, y = 0, y+1;

    def testTemplate(self, x, y, num):
        cvimg = self.__capture();
        if(None==cvimg):
            return;
        imgx, imgy = (28+6*x)*8, (9+(y<<1))*16;
        img = cvimg[imgy:imgy+16, imgx:imgx+40];
        template = self.__numberTemplate[num];
        print(self.__matchTemplateExact(img, template));

    def getBoard(self):
        cvimg = self.__capture();
        if(cvimg is None):
            return None;
        result = [];
        for y in range(4):
            for x in range(4):
                imgx, imgy = (28+6*x)*8, (9+(y<<1))*16;
                img = cvimg[imgy:imgy+16, imgx:imgx+40];
                self.__processImg(img);
                num = self.__getNum(img);
                if (None == num):
                    return None;
                result.append(num);
        return result;

