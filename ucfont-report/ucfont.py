import os
import struct
import mmap

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

    def __move_to(self):
        x=self.__data.read8()
        y=self.__data.read8()
        self.__path.on_move(x,y)

    def __hor(self):
        self.__path.on_hor(self.__data.read8())

    def __ver(self):
        self.__path.on_ver(self.__data.read8())

    def __line(self):
        self.__path.on_line(self.__data.read8(),self.__data.read8())

    def __qcurve(self):
        n=[self.__data.read8() for i in range(4)]
        self.__path.on_qcurve(*n)

    def __ccurve(self):
        n=[self.__data.read8() for i in range(6)]
        self.__path.on_ccurve(*n)

    def __rect(self):
        n=[self.__data.read8() for i in range(4)]
        self.__path.on_rect(*n)

    def __line_rx(self):
        self.__path.on_line_rx(self.__data.read4(),self.__data.read8())

    def __line_ry(self):
        self.__path.on_line_ry(self.__data.read8(),self.__data.read4())

    def __line_r4(self):
        self.__path.on_line_rel(self.__data.read4(),self.__data.read4())

    def __line_r6(self):
        x,y=self.__data.read6()
        self.__path.on_line_rel(x,y)

    def __qcurve_r4(self):
        x0,y0=self.__data.read4(),self.__data.read4()
        x1,y1=self.__data.read4(),self.__data.read4()
        self.__path.on_qcurve_rel(x0,y0,x0+x1,y0+y1)

    def __qcurve_r6(self):
        x0,y0=self.__data.read6()
        x1,y1=self.__data.read6()
        self.__path.on_qcurve_rel(x0,y0,x0+x1,y0+y1)

    def __ccurve_r4(self):
        x0,y0=self.__data.read4(),self.__data.read4()
        x1,y1=self.__data.read4(),self.__data.read4()
        x2,y2=self.__data.read4(),self.__data.read4()
        self.__path.on_ccurve_rel(x0,y0,x0+x1,y0+y1,x0+x1+x2,y0+y1+y2)

    def __ccurve_r6(self):
        x0,y0=self.__data.read6()
        x1,y1=self.__data.read6()
        x2,y2=self.__data.read6()
        self.__path.on_ccurve_rel(x0,y0,x0+x1,y0+y1,x0+x1+x2,y0+y1+y2)

    def __read(self):
        self.__path.on_read(self.__data.read8(),self.__data.read8())

    def parse(self):
        while not self.__data.is_end:
            self.__cmd[self.__data.readcmd()]()
        self.__path.on_end()


class Path:
    def __init__(self):
        self._x=0
        self._y=0

    def on_read(self,x,y):
        pass

    def on_rect(self,x0,y0,x1,y1):
        pass

    def on_move(self,x,y):
        self._x,self._y=x,y

    def on_hor(self,x):
        self._x=x

    def on_ver(self,y):
        self._y=y

    def on_line(self,x,y):
        self._x,self._y=x,y

    def on_qcurve(self,x0,y0,x1,y1):
        self._x,self._y=x1,y1

    def on_ccurve(self,x0,y0,x1,y1,x2,y2):
        self._x,self._y=x2,y2

    def on_line_rx(self,rx,y):
        self._x+=rx
        self._y=y

    def on_line_ry(self,x,ry):
        self._x=x
        self._y+=ry

    def on_line_rel(self,rx,ry):
        self._x+=rx
        self._y+=ry

    def on_qcurve_rel(self,x0,y0,x1,y1):
        self._x+=x1
        self._y+=y1

    def on_ccurve_rel(self,x0,y0,x1,y1,x2,y2):
        self._x+=x2
        self._y+=y2

    def on_end(self):
        pass


class UCFont:
    BASE_SIZE=256
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


class UCFontHZ(UCFont):
    BASE_SIZE=170
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
                font_file_sel=font_file
                self.font_idx=idx
                self.font_name=font_name
                super().__init__(os.path.join(font_path,font_file))
        if font_file_sel is None:
            raise IndexError(f'Font id {idx_in} not exist')

    def get_glyph(self,path_obj,qu:int,wei:int):
        return super().get_glyph(path_obj,(qu-0xb0)*94+(wei-0xa1))


class UCFontHZGBK(UCFont):
    BASE_SIZE=170
    def __init__(self,font_file):
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

