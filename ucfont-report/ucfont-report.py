import os
from ucfont import UCFontHZ
from ucfont import Path


class PathChecker(Path):
    def __check_pos(self):
        if self._x<0 or self._x>255:
            raise ValueError(f'X pos out of range: {self._x}')
        if self._y<0 or self._y>255:
            raise ValueError(f'Y pos out of range: {self._y}')

    def on_line_rx(self,rx,y):
        super().on_line_rx(rx,y)
        self.__check_pos()

    def on_line_ry(self,x,ry):
        super().on_line_ry(x,ry)
        self.__check_pos()

    def on_line_rel(self,rx,ry):
        super().on_line_rel(rx,ry)
        self.__check_pos()

    def on_qcurve_rel(self,x0,y0,x1,y1):
        super().on_qcurve_rel(x0,y0,x1,y1)
        self.__check_pos()

    def on_ccurve_rel(self,x0,y0,x1,y1,x2,y2):
        super().on_ccurve_rel(x0,y0,x1,y1,x2,y2)
        self.__check_pos()


class HZGB2312:
    def __init__(self):
        self.__qu=0xb0
        self.__wei=0xa1

    def __iter__(self):
        return self

    def __next__(self):
        self.__wei+=1
        if (self.__qu==0xd7 and self.__wei>=0xfa) or self.__wei>0xfe:
            self.__wei=0xa1
            self.__qu+=1
            if self.__qu>0xf7:
                raise StopIteration
        return self.__qu,self.__wei,bytes((self.__qu,self.__wei)).decode('gbk')


class FontChecker:
    def check_char(self,font,qu,wei,char):
        try:
            path=PathChecker()
            res=font.get_glyph(path,qu,wei)
            if res is None:
                self.normal=False
                self.missing.append(char)
        except ValueError as e:
            self.normal=False
            self.readfail.append(char)
        except IndexError as e:
            self.normal=False
            self.corrupt.append(char)

    def run(self,font_id,font_name):
        self.normal=True
        self.missing=[]
        self.readfail=[]
        self.corrupt=[]
        try:
            with UCFontHZ(font_id,'fnt') as font:
                for qu,wei,char in HZGB2312():
                    self.check_char(font,qu,wei,char)
            if self.normal:
                print(f'{font_id}:{font.font_name}：正常')
                return
            report=[]
            if len(self.missing):
                report.append(f'缺字：{len(self.missing)}')
            if len(self.readfail):
                report.append(f'读取失败：{len(self.readfail)}')
            if len(self.corrupt):
                report.aopend(f'数据损坏：{len(self.corrupt)}')
            print(f'{font_id}:{font_name}：{'，'.join(report)}')
        except FileNotFoundError as e:
            print(f'{font_id}:{font_name}：字库文件不存在')


class MainProc:
    def run(self):
        for font_id,font_name,font_file in UCFontHZ.FONT_LIST:
            checker=FontChecker()
            checker.run(font_id,font_name)
        return 0


if __name__=='__main__':
    mainProc=MainProc()
    exit(mainProc.run())

