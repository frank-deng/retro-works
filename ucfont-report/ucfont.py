import os
import struct
import mmap
import cairo


class Logger:
    def __init__(self,fpath='ucfont.log'):
        with open(fpath,'w') as fp:
            fp.write('')
        self.__fp=open(fpath,'a')

    def __enter__(self):
        return self

    def __exit__(self,exc_type,exc_val,exc_tb):
        self.close()
        return False

    def __del__(self):
        self.close()

    def close(self):
        if hasattr(self, '__fp') and self.__fp:
            try:
                self.__fp.close()
            except:
                pass
            self.__fp=None

    def write(self,_str):
        print(_str)
        self.__fp.write(_str+'\n')
        self.__fp.flush()


class BinLoader:
    def __init__(self,fpath):
        if not os.path.isfile(fpath):
            raise FileNotFoundError(f'File not exist {fpath}')
        self._file=open(fpath,'rb')
        self._mm=mmap.mmap(self._file.fileno(),0,access=mmap.ACCESS_READ)

    def __enter__(self):
        return self

    def __exit__(self,exc_type,exc_val,exc_tb):
        self.close()
        return False

    def __del__(self):
        self.close()

    def close(self):
        if hasattr(self, '_mm') and self._mm:
            try:
                self._mm.close()
            except:
                pass
            self._mm=None
        if hasattr(self, '_file') and self._file:
            try:
                self._file.close()
            except:
                pass
            self._file=None


class UCFontHZK16(BinLoader):
    def get_data(self,qu:int,wei:int):
        offset=((qu-0xa1)*94+(wei-0xa1))*32
        data=self._mm[offset:offset+32]
        if all(n==0 for n in data):
            return None
        return data


class Path:
    def on_read(self,x,y):
        pass

    def on_rect(self,x0,y0,x1,y1):
        pass

    def on_move(self,x,y):
        pass

    def on_line(self,x,y):
        pass

    def on_qcurve(self,x0,y0,x1,y1):
        pass

    def on_ccurve(self,x0,y0,x1,y1,x2,y2):
        pass

    def on_end(self):
        pass


class DataReader:
    def __init__(self,data):
        self.__data=data
        self.__offset=0

    def __read(self):
        val=self.__data[self.__offset>>1]
        if self.__offset & 1:
            val=(val>>4)&0xf
        else:
            val=val&0xf
        self.__offset+=1
        return val

    def readcmd(self):
        return self.__read()

    def read4(self):
        val=self.__read()
        if not (val & 0x8):
            return val
        return -(val&0x7)

    def read8(self):
        val0=self.__read()
        val1=self.__read()
        return (val0<<4)|val1

    def read6(self):
        d0=self.__read()
        d1=self.__read()
        d2=self.__read()
        res0=((d0<<2)&0x3c)|(d1>>2)
        res1=((d1<<4)&0x30)|d2
        if res0 & 0x20:
            res0=-(res0&0x1f)
        if res1 & 0x20:
            res1=-(res1&0x1f)
        return res0,res1

    @property
    def is_end(self):
        return self.__offset>=(len(self.__data)*2-1)


class UCFontCharProc:
    def __init__(self,path,data):
        self.__data=DataReader(data)
        self.__path=path
        self.__cmd={
            0:self.__move_to,
            1:self.__hor,
            2:self.__ver,
            3:self.__line,
            4:self.__qcurve,
            5:self.__ccurve,
            6:self.__rect,
            7:self.__line_rx,
            8:self.__line_ry,
            9:self.__line_r4,
            10:self.__line_r6,
            11:self.__qcurve_r4,
            12:self.__qcurve_r6,
            13:self.__ccurve_r4,
            14:self.__ccurve_r6,
            15:self.__read,
        }
        self.__x,self.__y=0,0

    def __move_to(self):
        self.__x=self.__data.read8()
        self.__y=self.__data.read8()
        self.__path.on_move(self.__x,self.__y)

    def __hor(self):
        self.__x=self.__data.read8()
        self.__path.on_line(self.__x,self.__y)

    def __ver(self):
        self.__y=self.__data.read8()
        self.__path.on_line(self.__x,self.__y)

    def __line(self):
        self.__x=self.__data.read8()
        self.__y=self.__data.read8()
        self.__path.on_line(self.__x,self.__y)

    def __qcurve(self):
        cx=self.__data.read8()
        cy=self.__data.read8()
        self.__x=self.__data.read8()
        self.__y=self.__data.read8()
        self.__path.on_qcurve(cx,cy,self.__x,self.__y)

    def __ccurve(self):
        cx0=self.__data.read8()
        cy0=self.__data.read8()
        cx1=self.__data.read8()
        cy1=self.__data.read8()
        self.__x=self.__data.read8()
        self.__y=self.__data.read8()
        self.__path.on_ccurve(cx0,cy0,cx1,cy1,self.__x,self.__y)

    def __rect(self):
        n=[self.__data.read8() for i in range(4)]
        self.__path.on_rect(*n)

    def __line_rx(self):
        self.__x+=self.__data.read4()
        self.__y=self.__data.read8()
        self.__path.on_line(self.__x,self.__y)

    def __line_ry(self):
        self.__x=self.__data.read8()
        self.__y+=self.__data.read4()
        self.__path.on_line(self.__x,self.__y)

    def __line_r4(self):
        self.__x+=self.__data.read4()
        self.__y+=self.__data.read4()
        self.__path.on_line(self.__x,self.__y)

    def __line_r6(self):
        x,y=self.__data.read6()
        self.__x+=x
        self.__y+=y
        self.__path.on_line(self.__x,self.__y)

    def __qcurve_r4(self):
        x0,y0=self.__data.read4(),self.__data.read4()
        x1,y1=self.__data.read4(),self.__data.read4()
        self.__path.on_qcurve(self.__x+x0,self.__y+y0,self.__x+x0+x1,self.__y+y0+y1)
        self.__x+=x0+x1
        self.__y+=y0+y1

    def __qcurve_r6(self):
        x0,y0=self.__data.read6()
        x1,y1=self.__data.read6()
        self.__path.on_qcurve(self.__x+x0,self.__y+y0,self.__x+x0+x1,self.__y+y0+y1)
        self.__x+=x0+x1
        self.__y+=y0+y1

    def __ccurve_r4(self):
        x0,y0=self.__data.read4(),self.__data.read4()
        x1,y1=self.__data.read4(),self.__data.read4()
        x2,y2=self.__data.read4(),self.__data.read4()
        self.__path.on_ccurve(self.__x+x0,self.__y+y0,self.__x+x0+x1,self.__y+y0+y1,
                              self.__x+x0+x1+x2,self.__y+y0+y1+y2)
        self.__x+=x0+x1+x2
        self.__y+=y0+y1+y2

    def __ccurve_r6(self):
        x0,y0=self.__data.read6()
        x1,y1=self.__data.read6()
        x2,y2=self.__data.read6()
        self.__path.on_ccurve(self.__x+x0,self.__y+y0,self.__x+x0+x1,self.__y+y0+y1,
                              self.__x+x0+x1+x2,self.__y+y0+y1+y2)
        self.__x+=x0+x1+x2
        self.__y+=y0+y1+y2

    def __read(self):
        self.__path.on_read(self.__data.read8(),self.__data.read8())

    def parse(self):
        while not self.__data.is_end:
            self.__cmd[self.__data.readcmd()]()
        self.__path.on_end()


class UCFont(BinLoader):
    BASE_SIZE=167
    def __init__(self,font_file):
        super().__init__(font_file)
        self.font_name=os.path.basename(font_file)

    def get_glyph(self,path_obj,idx:int):
        offset,datalen=struct.unpack('IH',self._mm[idx*6:(idx+1)*6])
        offset=offset&0xfffffff
        if (offset+datalen-1)>=len(self._mm):
            raise ValueError(f'Offset 0x{offset:x}, length {datalen} exceeds EOF.')
        if datalen==0:
            return None
        data=self._mm[offset:offset+datalen]
        if len(data)==0 or not data:
            return None
        parser=UCFontCharProc(path_obj,data)
        parser.parse()
        return path_obj


class UCFontT(UCFont):
    def __init__(self,font_file='HZKPST'):
        super().__init__(font_file)
        self.font_name='符号字库'

    def get_glyph(self,path_obj,qu:int,wei:int):
        return super().get_glyph(path_obj,(qu-0xa1)*94+(wei-0xa1))


class UCFontHZ(UCFont):
    FONT_LIST=(
        (0,'宋体简','HZKPSSTJ'),
        (1,'仿宋简','HZKPSFSJ'),
        (2,'黑体简','HZKPSHTJ'),
        (3,'楷体简','HZKPSKTJ'),
        (4,'标宋简','HZKPSXBJ'),
        (5,'报宋简','HZKPSBSJ'),
        (6,'细圆简','HZKPSY1J'),
        (7,'准圆简','HZKPSY3J'),
        (8,'隶变简','HZKPSLBJ'),
        (9,'大黑简','HZKPSDHJ'),
        (10,'魏碑简','HZKPSWBJ'),
        (11,'行楷简','HZKPSXKJ'),
        (12,'隶书简','HZKPSLSJ'),
        (13,'姚体简','HZKPSYTJ'),
        (14,'美黑简','HZKPSMHJ'),
        (20,'宋体繁','HZKPSSTF'),
        (21,'仿宋繁','HZKPSFSF'),
        (22,'黑体繁','HZKPSHTF'),
        (23,'楷体繁','HZKPSKTF'),
        (24,'标宋繁','HZKPSXBF'),
        (25,'秀丽繁','HZKPSXLF'),
        (26,'细圆繁','HZKPSY1F'),
        (27,'准圆繁','HZKPSY3F'),
        (28,'隶变繁','HZKPSLBF'),
        (29,'大黑繁','HZKPSDHF'),
        (30,'魏碑繁','HZKPSWBF'),
        (31,'行楷繁','HZKPSXKF'),
        (32,'琥珀繁','HZKPSHPF'),
        (33,'综艺繁','HZKPSZYF'),
    )
    def __init__(self,idx_in,font_path=''):
        font_file_sel=None
        for idx,font_name,font_file in self.__class__.FONT_LIST:
            if idx==idx_in:
                super().__init__(os.path.join(font_path,font_file))
                font_file_sel=font_file
                self.font_idx=idx
                self.font_name=font_name
        if font_file_sel is None:
            raise IndexError(f'Font id {idx_in} not exist')

    def get_glyph(self,path_obj,qu:int,wei:int):
        return super().get_glyph(path_obj,(qu-0xb0)*94+(wei-0xa1))


class UCFontGBK(UCFont):
    def __init__(self,font_file='HZKPSST.GBK'):
        super().__init__(font_file)
        self.font_name='宋体GBK'

    def get_glyph(self,path_obj,qu:int,wei:int):
        if qu<0x81 or qu>0xfe or wei<0x40 or wei==0x7f or wei>0xfe:
            return None
        if wei<0x7f:
            idx=0x2e44+(qu-0x81)*96+(wei-0x40)
        elif wei<0xa1:
            idx=0x2e44+(qu-0x81)*96+(wei-0x41)
        elif qu<0xa1:
            idx=0x2284+(qu-0x81)*94+(wei-0xa1)
        else:
            idx=(qu-0xa1)*94+(wei-0xa1)
        return super().get_glyph(path_obj,idx)


class PathChecker(Path):
    def __init__(self):
        self._l=None
        self._r=None
        self._t=None
        self._b=None

    def __check_pos(self,x,y):
        if x<0 or x>255:
            raise ValueError(f'X pos out of range: {x}')
        if y<0 or y>255:
            raise ValueError(f'Y pos out of range: {y}')
        if self._l is None or self._l>x:
            self._l=x
        if self._r is None or self._r<x:
            self._r=x
        if self._t is None or self._t>y:
            self._t=y
        if self._b is None or self._b<y:
            self._b=y

    def on_rect(self,x0,y0,x1,y1):
        self.__check_pos(x0,y0)
        self.__check_pos(x1,y1)

    def on_move(self,x,y):
        self.__check_pos(x,y)

    def on_line(self,x,y):
        self.__check_pos(x,y)

    def on_qcurve(self,x0,y0,x1,y1):
        self.__check_pos(x1,y1)

    def on_ccurve(self,x0,y0,x1,y1,x2,y2):
        self.__check_pos(x2,y2)

    def bounding_rect(self):
        return self._l,self._r,self._t,self._b


class PathCairo(PathChecker):
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
        x,y=self._get_xy(x,y)
        self._ctx.move_to(x,y)

    def on_line(self,x,y):
        super().on_line(x,y)
        x,y=self._get_xy(x,y)
        self._ctx.line_to(x,y)

    def on_qcurve(self,x0,y0,x1,y1):
        super().on_qcurve(x0,y0,x1,y1)
        cx,cy=self._get_xy(x0,y0)
        x,y=self._get_xy(x1,y1)
        self._qcurve_to(cx,cy,x,y)

    def on_ccurve(self,x0,y0,x1,y1,x2,y2):
        super().on_ccurve(x0,y0,x1,y1,x2,y2)
        cx0,cy0=self._get_xy(x0,y0)
        cx1,cy1=self._get_xy(x1,y1)
        x,y=self._get_xy(x2,y2)
        self._ctx.curve_to(cx0,cy0,cx1,cy1,x,y)

    def on_end(self):
        self._ctx.close_path()
        self._ctx.fill_preserve()
        self._ctx.stroke()


class IterHZGBK:
    def __init__(self):
        self.__qu=0x81
        self.__wei=0x39

    def __iter__(self):
        return self

    def __next_wei(self):
        self.__wei+=1
        if self.__wei==0x7f:
            self.__wei+=1
        if self.__wei>0xfe:
            self.__wei=0x40
            self.__qu+=1
            if self.__qu>0xf7:
                raise StopIteration

    def __next__(self):
        char=None
        while self.__qu<=0xf7:
            try:
                self.__next_wei()
                char=bytes((self.__qu,self.__wei)).decode('gbk')
                break
            except UnicodeDecodeError:
                pass
        return self.__qu,self.__wei,char


class FontReport:
    WEI_CNT=94
    COLS=20
    ROWS=5
    QU_GRP=9
    @staticmethod
    def bounding_rect_info():
        path=PathChecker()
        with UCFontT('fnt/HZKPST') as font:
            for wei in range(0xa1,0xff):
                font.get_glyph(path,0xa9,wei)
        return path.bounding_rect()

    @staticmethod
    def _draw_hzk16(ctx,x0,y0,data):
        for y in range(16):
            for i in range(8):
                mask=1<<(7-i)
                if data[y*2]&mask:
                    ctx.rectangle(x0+i,y0+y,1,1)
                if data[y*2+1]&mask:
                    ctx.rectangle(x0+i+8,y0+y,1,1)
        ctx.fill()

    def __init__(self,hzk16,font):
        self._hzk16=hzk16
        self._font=font
        self._missing=[]
        self._readfail=[]
        self._corrupt=[]

    def _draw_char(self,ctx,x,y,qu,wei):
        try:
            char=bytes((qu,wei)).decode('gbk')
            hzk16data=self._hzk16.get_data(qu,wei)
            if hzk16data is None:
                return
            self.__class__._draw_hzk16(ctx,x,y,hzk16data)
            path=PathCairo(ctx,x+16,y,48/self._font.BASE_SIZE,48/self._font.BASE_SIZE)
            if self._font.get_glyph(path,qu,wei) is None:
                self._missing.append(char)
        except UnicodeDecodeError:
            pass
        except ValueError as e:
            self._readfail.append(char)
        except IndexError as e:
            self._corrupt.append(char)

    def _draw_group(self,qu_start,idx=None):
        qu_cnt=min(self.QU_GRP,(1+0xf7-qu_start))
        surface=cairo.ImageSurface(cairo.FORMAT_A1,self.COLS*(48+16),self.ROWS*48*qu_cnt)
        ctx=cairo.Context(surface)
        ctx.set_source_rgba(1,1,1,1)
        for i in range(qu_cnt):
            for wei in range(0xa1,0xff):
                qu=qu_start+i
                x=((wei-0xa1)%self.COLS)*64
                y=(i*self.ROWS+int((wei-0xa1)/self.COLS))*48
                self._draw_char(ctx,x,y,qu,wei)
        font_idx,png_idx='',''
        if isinstance(self._font,UCFontHZ):
            font_idx=f'{self._font.font_idx:02d}'
        if idx is not None:
            png_idx=f"_{idx}"
        surface.write_to_png(f"{font_idx}{self._font.font_name}{png_idx}.png")
        surface.finish()

    def _check_font_gbk(self):
        for qu,wei,char in IterHZGBK():
            try:
                path=PathChecker()
                if self._font.get_glyph(path,qu,wei) is None:
                    self._missing.append(char)
            except ValueError as e:
                self._readfail.append(char)
            except IndexError as e:
                self._corrupt.append(char)


    def run(self):
        if isinstance(self._font,UCFontT):
            self._draw_group(0xa1)
        elif isinstance(self._font,UCFontHZ):
            for qu in range(0xb0,0xf7+1,self.QU_GRP):
                self._draw_group(qu,int((qu-0xb0)/self.QU_GRP))
        elif isinstance(self._font,UCFontGBK):
            self._check_font_gbk()

    def __str__(self):
        res=f'{self._font.font_name}：'
        if hasattr(self._font,'font_idx'):
            res=f'{self._font.font_idx:02d}#{self._font.font_name}：'
        report=[]
        if len(self._missing):
            report.append(f'缺字{len(self._missing)}个')
        if len(self._readfail):
            report.append(f'读取失败{len(self._readfail)}个')
        if len(self._corrupt):
            report.append(f'数据损坏{len(self._corrupt)}个')
        if len(report)==0:
            res+='正常'
        else:
            res+='，'.join(report)
        return res


def do_report(logger,hzk16):
    try:
        with UCFontGBK('fnt/HZKPSST.GBK') as font:
            report=FontReport(hzk16,font)
            report.run()
            logger.write(str(report))
    except FileNotFoundError as e:
        logger.write(f'字库文件HZKPSST.GBK不存在')

    try:
        with UCFontT('fnt/HZKPST') as font:
            report=FontReport(hzk16,font)
            report.run()
            logger.write(str(report))
        l,r,t,b=FontReport.bounding_rect_info()
        logger.write(f'字符基准尺寸：{r}x{b}，基准偏移：({l},{t})')
    except FileNotFoundError as e:
        logger.write(f'符号字库文件HZKPST不存在')

    for font_id,font_name,font_file in UCFontHZ.FONT_LIST:
        try:
            with UCFontHZ(font_id,'fnt') as font:
                report=FontReport(hzk16,font)
                report.run()
                logger.write(str(report))
        except FileNotFoundError as e:
            logger.write(f'{font_id:02d}#{font_name}：字库文件不存在')


def main():
    with Logger() as logger:
        with UCFontHZK16('fnt/HZK16') as hzk16:
            do_report(logger,hzk16)
    return 0

if __name__=='__main__':
    try:
        exit(main())
    except KeyboardInterrupt:
        exit(1)

