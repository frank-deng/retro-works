import asyncio
import os
import sys
import pwd
import pty
import fcntl
import termios
import struct
from util import Logger
from util.tcpserver import ReaderWrapper,WriterWrapper


async def readline(reader,writer,*,timeout=120,size=70,echo=True):
    inp,inp_len=bytearray(size),0

    async def read_char():
        char=None
        while char is None:
            char=await asyncio.wait_for(reader.read(1),timeout=timeout)
        return char

    async def handle_backspace():
        nonlocal inp_len
        if inp_len<=0:
            return
        inp_len-=1
        if echo:
            writer.write(b'\x08 \x08')
            await writer.drain()

    async def handle_char(char):
        nonlocal inp_len
        val=int.from_bytes(char,'little')
        if val>=0x20 and val<=0x7e and inp_len<size:
            inp[inp_len]=val
            inp_len+=1
            if echo:
                writer.write(char)
                await writer.drain()

    res=None
    while True:
        char=await read_char()
        if char==b'': #Disconnected
            inp_len=None
            break
        elif char in (b'\x0d',b'\x0a'): #Finished
            writer.write(b'\r\n')
            await writer.drain()
            break
        elif b'\x08'==char: #Backspace
            await handle_backspace()
        else:
            await handle_char(char)

    if inp_len is not None:
        res=bytes(inp[:inp_len])
        # Ignore input after Enter as much as possible
        try:
            await asyncio.wait_for(reader.read(1000),timeout=0.1)
        except asyncio.TimeoutError:
            pass
    return res


async def login(reader,writer):
    username=b''
    while username==b'':
        writer.write(b'\r\nLogin:')
        await writer.drain()
        username=await readline(reader,writer,echo=True)
    if username is None:
        return None,None
    writer.write(b'Password:')
    await writer.drain()
    password=await readline(reader,writer,echo=False)
    if password is None:
        return None,None
    return username,password


class TelnetWriterWrapper(WriterWrapper):
    def write(self,chunk):
        super().write(chunk.replace(b'\xff',b'\xff\xff'))


class TelnetReaderWrapper(ReaderWrapper):
    ST_DATA=0
    ST_IAC=1
    ST_SB=2
    ST_SB_IAC=3
    BYTE_IAC=0xff
    def __init__(self,reader):
        super().__init__(reader)
        self.__stat_func={
            self.ST_DATA:self.__proc_data,
            self.ST_IAC:self.__proc_iac,
            self.ST_SB:self.__proc_sb,
            self.ST_SB_IAC:self.__proc_data,
        }
        self.__stat=self.ST_DATA
        self.__res=bytearray()
        self.__buf=bytearray()
        self.__idx=0
        self.__buflen=0
        self.__running=True

    def __proc_data(self):
        iac_pos=self.__buf.find(self.BYTE_IAC,self.__idx)
        if iac_pos<0:
            self.__res.extend(self.__buf[self.__idx:])
            self.__idx=self.__buflen
        else:
            self.__res.extend(self.__buf[self.__idx:iac_pos])
            self.__idx=iac_pos+1
            self.__stat=self.ST_IAC

    def __proc_iac(self):
        b=self.__buf[self.__idx]
        if b==self.BYTE_IAC:
            self.__res.append(self.BYTE_IAC)
            self.__stat=self.ST_DATA
            self.__idx+=1
        elif b==0xFA:
            self.__stat=self.ST_SB
            self.__idx+=1
        elif b in (0xFB,0xFC,0xFD,0xFE):
            if self.__idx+1>=self.__buflen:
                return 1
            self.__idx+=2
            self.__stat=self.ST_DATA
        else:
            self.__idx+=1
            self.__stat=self.ST_DATA

    def __proc_sb(self):
        iac_pos=self.__buf.find(self.BYTE_IAC,self.__idx)
        if iac_pos==-1:
            self.__idx=self.__buflen
        else:
            self.__idx+=1
            self.__stat=self.ST_SB_IAC

    def __proc_sb_iac(self):
        b=self.__buf[self.__idx]
        if b==0xF0:
            self.__stat=self.ST_DATA
        else:
            self.__stat=self.ST_SB
        self.__idx+=1

    def __feed(self,data):
        self.__running=True
        self.__buf.extend(data)
        self.__idx,self.__buflen,res=0,len(self.__buf),bytearray()
        while self.__idx<self.__buflen:
            if self.__stat_func[self.__stat]() is not None:
                break
        if self.__idx>=self.__buflen:
            self.__buf.clear()
        else:
            del self.__buf[:self.__idx]
        res=bytes(self.__res)
        self.__res.clear()
        return res

    async def read(self,n=-1):
        res=b''
        while not res:
            data=await super().read(n)
            if not data:
                return data
            res=self.__feed(data)
        return res


async def TelnetWrapper(reader,writer):
    writer.write(b'\xFF\xFD\x22\xFF\xFB\x01\xFF\xFB\x00\xFF\xFD\x00\r\n')
    await writer.drain()
    return TelnetReaderWrapper(reader),TelnetWriterWrapper(writer)

