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

    def _get_xy(self,x,y):
        return int(self._xorig+x*self._sx), int(self._yorig+y*self._sy)

    def __init__(self,ctx,x0,y0,sx,sy):
        super().__init__()
        self._ctx=ctx
        self._ctx.set_fill_rule(cairo.FILL_RULE_WINDING)
        self._ctx.new_path()
        self._xorig,self._yorig=x0,y0
        self._sx,self._sy=sx,sy

    def on_rect(self,x0,y0,x1,y1):
        super().on_rect(x0,y0,x1,y1)
        x0,y0=self._get_xy(x0,y0)
        x1,y1=self._get_xy(x1,y1)
        self._ctx.rectangle(x0,y0,x1-x0,y1-y0)
        self._ctx.fill_preserve()

    def on_move(self,x,y):
        super().on_move(x,y)
        x,y=self._get_xy(self._x,self._y)
        self._ctx.move_to(x,y)

    def on_hor(self,x):
        super().on_hor(x)
        x,y=self._get_xy(self._x,self._y)
        self._ctx.line_to(x,y)

    def on_ver(self,y):
        super().on_ver(y)
        x,y=self._get_xy(self._x,self._y)
        self._ctx.line_to(x,y)

    def on_line(self,x,y):
        super().on_line(x,y)
        x,y=self._get_xy(self._x,self._y)
        self._ctx.line_to(x,y)

    def on_qcurve(self,x0,y0,x1,y1):
        cx,cy=self._get_xy(x0,y0)
        x,y=self._get_xy(x1,y1)
        self._qcurve_to(cx,cy,x,y)
        super().on_qcurve(x0,y0,x1,y1)

    def on_ccurve(self,x0,y0,x1,y1,x2,y2):
        cx0,cy0=self._get_xy(x0,y0)
        cx1,cy1=self._get_xy(x1,y1)
        x,y=self._get_xy(x2,y2)
        self._ctx.curve_to(cx0,cy0,cx1,cy1,x,y)
        super().on_ccurve(x0,y0,x1,y1,x2,y2)

    def on_line_rx(self,rx,y):
        super().on_line_rx(rx,y)
        x,y=self._get_xy(self._x,self._y)
        self._ctx.line_to(x,y)

    def on_line_ry(self,x,ry):
        super().on_line_ry(x,ry)
        x,y=self._get_xy(self._x,self._y)
        self._ctx.line_to(x,y)

    def on_line_rel(self,rx,ry):
        super().on_line_rel(rx,ry)
        x,y=self._get_xy(self._x,self._y)
        self._ctx.line_to(x,y)

    def on_qcurve_rel(self,x0,y0,x1,y1):
        cx,cy=self._get_xy(self._x+x0,self._y+y0)
        x,y=self._get_xy(self._x+x1,self._y+y1)
        self._qcurve_to(cx,cy,x,y)
        super().on_qcurve_rel(x0,y0,x1,y1)

    def on_ccurve_rel(self,x0,y0,x1,y1,x2,y2):
        cx0,cy0=self._get_xy(self._x+x0,self._y+y0)
        cx1,cy1=self._get_xy(self._x+x1,self._y+y1)
        x,y=self._get_xy(self._x+x2,self._y+y2)
        self._ctx.curve_to(cx0,cy0,cx1,cy1,x,y)
        super().on_ccurve_rel(x0,y0,x1,y1,x2,y2)

    def on_end(self):
        self._ctx.close_path()
        self._ctx.fill_preserve()


def main():
    surface=cairo.ImageSurface(cairo.FORMAT_A1,48,48)
    ctx=cairo.Context(surface)
    ctx.set_source_rgba(1,1,1,1)
    with UCFontHZ(0,'fnt') as font:
        path=PathCairo(ctx,0,0,48/font.BASE_SIZE,48/font.BASE_SIZE)
        res=font.get_glyph(path,0xb0,0xa1)
    surface.write_to_png("1.png")
    surface.finish()

if __name__=='__main__':
    main()
