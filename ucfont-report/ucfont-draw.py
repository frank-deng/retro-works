import argparse
import cairo
import math
from ucfont import UCFontHZK16
from ucfont import UCFontHZ
from ucfont import UCFontT
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
        self._ctx.set_line_width(0.5)
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
        self._ctx.stroke()


def draw_hzk16(ctx,x0,y0,data):
    for y in range(16):
        for i in range(8):
            mask=1<<(7-i)
            if data[y*2]&mask:
                ctx.rectangle(x0+i,y0+y,1,1)
            if data[y*2+1]&mask:
                ctx.rectangle(x0+i+8,y0+y,1,1)
    ctx.fill()


WEI_CNT=94
COLS=20
ROWS=math.ceil(WEI_CNT/COLS)
QU_GRP=9


def draw_chars_symbols(font16,font):
    qu_cnt=0xa9-0xa1+1
    surface=cairo.ImageSurface(cairo.FORMAT_A1,COLS*(48+16),ROWS*48*qu_cnt)
    ctx=cairo.Context(surface)
    ctx.set_source_rgba(1,1,1,1)
    for qu in range(0xa1,0xa9+1):
        for wei in range(0xa1,0xff):
            x=((wei-0xa1)%COLS)*64
            y=((qu-0xa1)*ROWS+int((wei-0xa1)/COLS))*48
            draw_hzk16(ctx,x,y,font16.get_data(qu,wei))
            path=PathCairo(ctx,x+16,y,48/font.BASE_SIZE,48/font.BASE_SIZE)
            try:
                res=font.get_glyph(path,qu,wei)
            except (ValueError,IndexError) as e:
                pass
    surface.write_to_png(f"HZKPST.png")
    surface.finish()


def draw_chars_grp(font16,font,qu_start):
    idx=int((qu_start-0xb0)/QU_GRP)
    qu_cnt=min(QU_GRP,(1+0xf7-qu_start))
    surface=cairo.ImageSurface(cairo.FORMAT_A1,COLS*(48+16),ROWS*48*qu_cnt)
    ctx=cairo.Context(surface)
    ctx.set_source_rgba(1,1,1,1)
    for i in range(qu_cnt):
        for wei in range(0xa1,0xff):
            qu=qu_start+i
            x=((wei-0xa1)%COLS)*64
            y=(i*ROWS+int((wei-0xa1)/COLS))*48
            draw_hzk16(ctx,x,y,font16.get_data(qu,wei))
            path=PathCairo(ctx,x+16,y,48/font.BASE_SIZE,48/font.BASE_SIZE)
            try:
                res=font.get_glyph(path,qu,wei)
            except (ValueError,IndexError) as e:
                pass
    surface.write_to_png(f"{font.font_name}_{idx}.png")
    surface.finish()

def main():
    with UCFontHZK16('fnt/HZK16') as font16:
        with UCFontT('fnt/HZKPST') as font:
            draw_chars_symbols(font16,font)
        for font_id,font_name,font_file in UCFontHZ.FONT_LIST:
            try:
                with UCFontHZ(font_id,'fnt') as font:
                    for qu in range(0xb0,0xf7+1,QU_GRP):
                        draw_chars_grp(font16,font,qu)
            except FileNotFoundError as e:
                print(f'{font_id}#{font_name}：字库文件不存在')

if __name__=='__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
