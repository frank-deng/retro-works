import asyncio


async def readline(reader,writer,*,timeout=None,size=70,echo=True):
    inp,inp_len=bytearray(size),0

    async def read_char():
        char=None
        while char is None:
            if timeout is None:
                char=await reader.read(1)
            else:
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


async def login(reader,writer,*,timeout=None):
    username=b''
    while username==b'':
        writer.write(b'\r\nLogin:')
        await writer.drain()
        username=await readline(reader,writer,timeout=timeout,echo=True)
    if username is None:
        return None,None
    writer.write(b'Password:')
    await writer.drain()
    password=await readline(reader,writer,timeout=timeout,echo=False)
    if password is None:
        return None,None
    return username,password


async def login_loop(reader,writer,*,on_session,
                     login_retry=None,login_timeout=None,conn_counter=None):
    if conn_counter is not None and not conn_counter.try_acquire():
        writer.close()
        return
    try:
        login_failed=0
        while login_retry is None or login_failed<login_retry:
            username,password=await login(reader,writer,timeout=login_timeout)
            if username is None or password is None:
                break
            if not username:
                continue
            if not await on_session(reader,writer,
                                    username.decode(),password.decode()):
                login_failed+=1
                writer.write(b'Login Failed.\r\n')
                await asyncio.gather(writer.drain(),asyncio.sleep(1))
            else:
                login_failed=0
    finally:
        if conn_counter is not None:
            conn_counter.release()

