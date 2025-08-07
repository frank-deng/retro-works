#!/usr/bin/env python3

import asyncio
from util import Logger
from util.tcpserver import TCPServer
import time
from datetime import datetime


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


class CommandHandler(Logger):
    def __init__(self,reader,writer):
        self.__reader,self.__writer=reader,writer
        self.__cmdTable={
            'q':self.__quit,
            'quit':self.__quit,
            'date':self.__date,
            'boom':self.__boom
        }

    async def __quit(self,cmd):
        self.__writer.close()

    async def __date(self,cmd):
        formatted_date = "{:%Y-%m-%d %H:%M:%S}".format(datetime.now())
        await self.write(formatted_date+'\r\n')

    async def __boom(self,cmd):
        await self.write('BOOM!!!\r\n')
        while True:
            time.sleep(1)

    async def write(self,content):
        self.__writer.write(content.encode())
        await self.__writer.drain()

    async def run(self,cmd):
        if cmd not in self.__cmdTable:
            return
        handler=self.__cmdTable[cmd]
        await handler(cmd)


class TestServer(TCPServer):
    def __init__(self,config):
        super().__init__(config['port'])

    async def handler(self,reader,writer):
        try:
            cmdRunner=CommandHandler(reader,writer)
            while True:
                await cmdRunner.write('>')
                cmd=await readline(reader,writer)
                if cmd is None:
                    return
                await cmdRunner.run(cmd.decode())
        except asyncio.TimeoutError:
            pass

