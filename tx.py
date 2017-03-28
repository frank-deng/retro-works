import os, sys;

def Mode(mode):
    return 'M%d'%mode;

def Clrscr(n=None):
    return 'CL';

def Color(n):
    return 'CO%d'%n;

def EnableXORMode():
    return 'X1';

def DisableXORMode():
    return 'X0';

def SetStyle(n):
    return 'ST%d'%n;

def SetPattern(data):
    return 'ST13DS'+','.join([int(n) for n in data]);

def Dot(x,y):
    return 'D%d,%d'%(x,y);

def Line(x0,y0,x1,y1):
    return 'L%d,%d,%d,%d'%(x0,y0,x1,y1);

def LineTo(x,y):
    return 'LT%d,%d'%(x,y);

def Rect(x0,y0,x1,y1,fill=False):
	if fill:
        return 'B%d,%d,%d,%d'%(x0,y0,x1,y1);
	else:
        return 'R%d,%d,%d,%d'%(x0,y0,x1,y1);

def Circle(x,y,r,fill=False):
    if fill:
    	return 'E%d,%d,%d,%d,%d,%d,%d'%(x,y,0,360,r,r,2);
    else:
        return 'C%d,%d,%d'%(x,y,r);
        
def Arc(x,y,r,s,e):
	return 'E%d,%d,%d,%d,%d,%d,%d'%(x,y,s,e,r,r,0);
	
def Sector(x,y,r,s,e,fill=False):
	if fill:
	    return 'E%d,%d,%d,%d,%d,%d,%d'%(x,y,s,e,r,r,2);
	else:
		return 'E%d,%d,%d,%d,%d,%d,%d'%(x,y,s,e,r,r,1);

def Ellipse(x,y,a,b,fill=False):
	if fill:
        return 'E%d,%d,%d,%d,%d,%d,%d'%(x,y,0,360,a,b,2);
	else:
        return 'E%d,%d,%d,%d,%d,%d,%d'%(x,y,0,360,a,b,0);

def EllipticalArc(x,y,a,b,s,e):
	return 'E%d,%d,%d,%d,%d,%d,%d'%(x,y,s,e,a,b,0);

def EllipticalSector(x,y,a,b,s,e,fill=False):
	if fill:
        return 'E%d,%d,%d,%d,%d,%d,%d'%(x,y,s,e,a,b,2);
	else:
        return 'E%d,%d,%d,%d,%d,%d,%d'%(x,y,s,e,a,b,1);

def Fill(x,y,c):
    return 'F%d,%d,%d'%(x,y,c);

def RenderPCX(x,y,f):
    return 'RE%d,%d,%s'%(x,y,f);

def RenderPCXScaled(x,y,w,h,f):
    return 'RF%d,%d,%d,%d,%s'%(x,y,w,h,f);

def SetPCXRenderMode(mode):
    return 'PM%d'%mode;

def ProtectBasicPalette():
    return 'PP1';

def UnprotectBasicPalette():
    return 'PP0';

def ProtectPalette():
    return 'SP0';

def UnprotectPalette():
    return 'SP1';

def CopyScreen(x0,y0,x1,y1,x2,y2):
    return 'MI%d,%d,%d,%d,%d,%d'%(x0,y0,x1,y1,x2,y2);

def StopMusic():
    return 'SE';

def Pause():
    return 'WA';

def SetCursorSpeed(n):
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

