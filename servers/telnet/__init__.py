import asyncio
import os
import sys
import pwd
import pty
import fcntl
import termios
import struct
from util import Logger
from util.tcpserver import TCPServer


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


class ProcessHandler(Logger):
    __buf_size=4096
    __proc=None
    __master_fd=None
    __slave_fd=None
    __pty_reader=None
    __tasks=None
    def __init__(self,reader,writer,*,buf_size=4096):
        self.__reader,self.__writer=reader,writer
        self.__buf_size=buf_size
        self.__loop=asyncio.get_running_loop()
        self.__queue=asyncio.Queue()

    async def __aenter__(self):
        try:
            self.__master_fd,self.__slave_fd=pty.openpty()
            await self.create_subprocess_exec(self.__master_fd,self.__slave_fd)
            os.close(self.__slave_fd)
            os.set_blocking(self.__master_fd,False)
            self.__tasks=(
                asyncio.create_task(self.__pty_to_tcp()),
                asyncio.create_task(self.__tcp_to_pty())
            )
        except Exception as e:
            await self.__cleanup()
            raise
        return self

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        if self.__tasks is not None:
            await asyncio.wait(self.__tasks,return_when=asyncio.FIRST_COMPLETED)
        await self.__cleanup()

    def __fd_ready(self):
        try:
            data=os.read(self.__master_fd,self.__buf_size)
            if not data:
                self.__loop.call_soon(self.__queue.put_nowait,b"")
                return
            self.__queue.put_nowait(data)
        except (OSError,asyncio.CancelledError):
            self.__queue.put_nowait(b"")

    async def __pty_to_tcp(self):
        self.__loop.add_reader(self.__master_fd,self.__fd_ready)
        try:
            while True:
                data=await self.__queue.get()
                if not data:
                    break
                self.__writer.write(data)
                await self.__writer.drain()
        except (ConnectionResetError,asyncio.CancelledError):
            pass
        except Exception as e:
            self.logger.error(e,exc_info=True)
        finally:
            self.__loop.remove_reader(self.__master_fd)

    async def __write_fd(self,data):
        n=None
        while data:
            try:
                n=os.write(self.__master_fd,data)
                data=data[n:]
            except BlockingIOError:
                self.logger.debug(f'Partial data written {n}/{len(data)}')
                await asyncio.sleep(0.01)

    async def __tcp_to_pty(self):
        try:
            while True:
                data=await self.__reader.read(self.__buf_size)
                if not data:
                    break
                await self.__write_fd(data)
        except (ConnectionResetError,OSError,asyncio.CancelledError):
            pass
        except Exception as e:
            self.logger.error(e,exc_info=True)

    async def __cleanup(self):
        try:
            if self.__tasks is not None:
                for task in self.__tasks:
                    if not task.done():
                        task.cancel()
                await asyncio.gather(*self.__tasks)
        except Exception as e:
            self.logger.error(e,exc_info=True)
        finally:
            self.__close_fd(self.__master_fd)
            self.__master_fd=None

    def __close_fd(self,fd):
        try:
            if fd is not None:
                os.close(fd)
        except Exception as e:
            self.logger.error(e,exc_info=True)

    async def create_subprocess_exec(self,slave_fd):
        pass


