import argparse
import cairo
from ucfont import UCFontHZ
from ucfont import UCFontHZGBK
from ucfont import Path


class PathCairo(Path):
    def _qcurve_to(self,cx,cy,x,y):
        x0,y0=self._ctx.get_current_point()
        cx0,cy0=x0+(2.0/3.0)*(cx-x0),y0+(2.0/3.0)*(cy-y0)
        cx1,cy1=x+(2.0/3.0)*(cx-x),y+(2.0/3.0)*(cy-y)
        self._ctx.curve_to(cx0,cy0,cx1,cy1,x,y)

    def __init__(self,ctx,x0,y0,w,h):
        self._ctx=ctx
        self._xorig,self._yorig=x0,y0
        self._x,self._y=x0,y0
        self._ctx.new_path()

    def on_rect(self,x0,y0,x1,y1):
        pass

    def on_move(self,x,y):
        self._x,self._y=self._xorig+x,self._yorig+y
        self._ctx.move_to(self._x,self._y)

    def on_hor(self,x):
        self._x=self._xorig+x
        self._ctx.line_to(self._x,self._y)

    def on_ver(self,y):
        self._y=self._yorig+y
        self._ctx.line_to(self._x,self._y)

    def on_line(self,x,y):
        self._x,self._y=self._xorig+x,self._yorig+y
        self._ctx.line_to(self._x,self._y)

    def on_qcurve(self,x0,y0,x1,y1):
        self._x,self._y=self._xorig+x1,self._yorig+y1
        self._qcurve_to(self._xorig+x0,self._yorig+y0,self._x,self._y)

    def on_ccurve(self,x0,y0,x1,y1,x2,y2):
        self._x,self._y=self._xorig+x2,self._yorig+y2
        self._ctx.curve_to(
            self._xorig+x0,self._yorig+y0,
            self._xorig+x1,self._yorig+y1,
            self._x,self._y
        )

    def on_line_rx(self,rx,y):
        self._x+=rx
        self._y=self._yorig+y
        self._ctx.line_to(self._x,self._y)

    def on_line_ry(self,x,ry):
        self._x=self._xorig+x
        self._y+=ry
        self._ctx.line_to(self._x,self._y)

    def on_line_rel(self,rx,ry):
        self._x+=rx
        self._y+=ry
        self._ctx.line_to(self._x,self._y)

    def on_qcurve_rel(self,x0,y0,x1,y1):
        self._qcurve_to(self._x+x0,self._y+y0,self._x+x1,self._y+y1)
        self._x+=x1
        self._y+=y1

    def on_ccurve_rel(self,x0,y0,x1,y1,x2,y2):
        self._ctx.curve_to(
            self._x+x0,self._y+y0,
            self._x+x1,self._y+y1,
            self._x+x2,self._y+y2
        )
        self._x+=x2
        self._y+=y2

    def on_end(self):
        self._ctx.close_path()
        self._ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
        self._ctx.fill_preserve()


def main():
    surface=cairo.ImageSurface(cairo.FORMAT_A1,256,256)
    ctx=cairo.Context(surface)
    ctx.set_source_rgba(1,1,1,1)
    with UCFontHZ(0,'fnt') as font:
        path=PathCairo(ctx,0,0,32,32)
        res=font.get_glyph(path,0xb0,0xa1)
    surface.write_to_png("1.png")
    surface.finish()

if __name__=='__main__':
    main()
