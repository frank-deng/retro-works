import asyncio
from ..util.tcpserver import ReaderWrapper,WriterWrapper


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

