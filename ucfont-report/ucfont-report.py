import os
import sys
from ucfont import UCFontHZ
from ucfont import UCFontHZGBK
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


class HZGBK:
    def __init__(self):
        self.__qu=0x81
        self.__wei=0x40

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
        while True:
            try:
                self.__next_wei()
                char=bytes((self.__qu,self.__wei)).decode('gbk')
                break
            except UnicodeDecodeError:
                pass
        return self.__qu,self.__wei,char


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

    def run(self,font,iterchars=HZGB2312):
        self.normal=True
        self.missing=[]
        self.readfail=[]
        self.corrupt=[]
        if hasattr(font,'font_idx') and hasattr(font,'font_name'):
            print(f'{font.font_idx}#{font.font_name}：',end='')
        else:
            print(f'{font.font_name}：',end='')
        sys.stdout.flush()
        for qu,wei,char in iterchars():
            self.check_char(font,qu,wei,char)
        if self.normal:
            print('正常')
            return
        report=[]
        if len(self.missing):
            report.append(f'缺字{len(self.missing)}个')
        if len(self.readfail):
            report.append(f'读取失败{len(self.readfail)}个')
        if len(self.corrupt):
            report.aopend(f'数据损坏{len(self.corrupt)}个')
        print('，'.join(report))


class MainProc:
    def run(self):
        try:
            with UCFontHZGBK('fnt/HZKPSST.GBK') as font:
                checker=FontChecker()
                checker.run(font,HZGBK)
        except FileNotFoundError as e:
            print(f'HZKPSST.GBK字库文件不存在')
        for font_id,font_name,font_file in UCFontHZ.FONT_LIST:
            try:
                with UCFontHZ(font_id,'fnt') as font:
                    checker=FontChecker()
                    checker.run(font)
            except FileNotFoundError as e:
                print(f'{font_id}#{font_name}：字库文件不存在')
        return 0


if __name__=='__main__':
    mainProc=MainProc()
    exit(mainProc.run())

