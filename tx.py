import os, sys;
def M(mode):
    return 'M%d'%mode;

def CL(n=None):
    if (n):
        return 'CL%d'%n;
    else:
        return 'CL';

def CO(n):
    return 'CO%d'%n;

def SC(n):
    return 'SC%d'%n;

def X(n=False):
    if (n):
        return 'X1';
    else:
        return 'X0';

def ST(n):
    return 'SC%d'%n;

def DS(data):
    return 'DS'+','.join([int(n) for n in data]);

def D(x,y):
    return 'D%d,%d'%(x,y);

def L(x0,y0,x1,y1):
    return 'L%d,%d,%d,%d'%(x0,y0,x1,y1);

def LT(x,y):
    return 'LT%d,%d'%(x,y);

def R(x0,y0,x1,y1):
    return 'R%d,%d,%d,%d'%(x0,y0,x1,y1);

def B(x0,y0,x1,y1):
    return 'B%d,%d,%d,%d'%(x0,y0,x1,y1);

def C(x,y,r):
    return 'C%d,%d,%d'%(x,y,r);

def E(x,y,a,b,c,d,e):
    return 'E%d,%d,%d,%d,%d,%d,%d'%(x,y,a,b,c,d,e);

def F(x,y,c):
    return 'F%d,%d,%d'%(x,y,c);

def SA(x0,y0,x1,y1,f):
    return 'SA%d,%d,%d,%d,%s'%(x0,y0,x1,y1,f);

def RE(x,y,f):
    return 'RE%d,%d,%s'%(x,y,f);

def RP(x,y,w,h,f):
    return 'RP%d,%d,%d,%d,%s'%(x,y,w,h,f);

def RF(x,y,w,h,f):
    return 'RF%d,%d,%d,%d,%s'%(x,y,w,h,f);

def PM(mode):
    return 'PM%d'%mode;

def PP(n=True):
    if n:
        return 'PP1';
    else:
        return 'PP0';

def SP(n=True):
    if n:
        return 'SP1';
    else:
        return 'SP0';

def MI(x0,y0,x1,y1,x2,y2):
    return 'MI%d,%d,%d,%d,%d,%d'%(x0,y0,x1,y1,x2,y2);

def StopMusic():
    return 'SE';

def WA():
    return 'WA';

def CursorSpeed(n):
    return 'CU0,%d'%n;

def ShowCursor():
    return 'CU1,1CU2,1';

def HideCursor():
    return 'CU1,0CU2,0';

def ShowBar():
    return 'KB1,1';

def HideBar():
    return 'KB1,0';

def Music(notes):
    return 'SO'+notes;

class TX:
    __out = None;
    def __init__(__self, out = sys.stdout):
        __self.__out = out.fileno();
    def write(__self, data):
        if (isinstance(data, (list,tuple))):
            os.write(__self.__out, ('\x0E['+''.join(data)+']').encode('GBK'));
        elif (isinstance(data, str)):
            os.write(__self.__out, data.encode('GBK'));

