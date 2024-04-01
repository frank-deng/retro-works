#!/usr/bin/env python3

import asyncio,signal,json,hashlib,subprocess,pty,fcntl,os,time
from traceback import print_exc

pppdExec='/usr/sbin/pppd'
login_timeout=120
loginInfo={}
session_info={}

async def read_line(reader,writer,echo=True,max_len=1024):
    res=b''
    running=True
    while running:
        char=await asyncio.wait_for(reader.read(1), timeout=login_timeout)
        val=int.from_bytes(char,'little')
        if 0==val: #Connection closed
            raise BrokenPipeError
        elif 0x08==val and len(res)>0: #Backspace
            res=res[:-1]
            if(echo):
                writer.write(b'\x08 \x08')
                await writer.drain()
        elif 0x0d==val or 0x0a==val or 0==val: #Finished
            running=False
            writer.write(b'\r\n')
            await writer.drain()
        elif val>=0x20 and val<=0x7e and len(res)<max_len:
            res+=val.to_bytes(1,'little')
            if(echo):
                writer.write(val.to_bytes(1,'little'))
                await writer.drain()
    try:
        await asyncio.wait_for(reader.read(max_len), timeout=0.01)
    except asyncio.TimeoutError:
        pass
    return res

async def service_main(reader,writer):
    global loginInfo
    writer.write(b'\r\nLogin:')
    await writer.drain()
    username=await read_line(reader,writer,echo=True,max_len=80)
    if not username:
        return True
    writer.write(b'Password:')
    await writer.drain()
    password=await read_line(reader,writer,echo=False,max_len=80)
    username=username.decode('UTF-8')
    password=hashlib.sha256(password).hexdigest();
    __loginInfo=loginInfo.get(username)
    if __loginInfo is None or password != __loginInfo['password']:
        writer.write(b'Login Failed.\r\n')
        await writer.drain()
        return True
    elif username in session_info:
        writer_orig=session_info[username]
        session_info[username]=writer
        writer_orig.close()
        await writer_orig.wait_closed()
    else:
        session_info[username]=writer
    __master, __slave = pty.openpty()
    fcntl.fcntl(__master, fcntl.F_SETFL, fcntl.fcntl(__master, fcntl.F_GETFL) | os.O_NONBLOCK)
    fcntl.fcntl(__slave, fcntl.F_SETFL, fcntl.fcntl(__slave, fcntl.F_GETFL) | os.O_NONBLOCK)
    ptyPath="/proc/%d/fd/%d"%(os.getpid(),__slave)
    subprocess.Popen([pppdExec,ptyPath,] + __loginInfo['options'], bufsize=0, start_new_session=True,
        stdin=__slave, stdout=__slave, stderr=__slave)
    try:
        while not writer.is_closing():
            try:
                writer.write(os.read(__master, 1024))
            except BlockingIOError:
                pass
            try:
                content=await asyncio.wait_for(reader.read(1024), timeout=0.01)
                if not content:
                    raise BrokenPipeError
                os.write(__master, content)
            except asyncio.TimeoutError:
                pass
            except BlockingIOError:
                pass
    finally:
        os.close(__slave)
        os.close(__master)
        if username in session_info and session_info[username]==writer:
            del session_info[username]
    return False

async def service_handler(reader,writer):
    try:
        running=True
        while running:
            running=await service_main(reader,writer)
    except asyncio.TimeoutError:
        writer.write(b'\r\n\r\nTimeout!!\r\n')
    except ConnectionResetError:
        pass
    except BrokenPipeError:
        pass
    except Exception as e:
        print_exc()
    finally:
        if not writer.is_closing():
            writer.close()
            await writer.wait_closed()
		
async def main(host,port):
    server=await asyncio.start_server(service_handler,
        host=host,port=port,reuse_address=True,reuse_port=True)
    loop = asyncio.get_event_loop()
    for s in (signal.SIGINT, signal.SIGTERM, signal.SIGQUIT):
        loop.add_signal_handler(s, lambda: server.close())
    try:
        async with server:
            await server.serve_forever()
    except asyncio.exceptions.CancelledError:
        pass
    finally:
        await server.wait_closed()

if '__main__'==__name__:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host',
        '-H',
        help='Specify binding host for the telnetd server.',
        default=''
    )
    parser.add_argument(
        '--port',
        '-P',
        help='Specify port for the telnetd server.',
        type=int,
        default=23
    )
    parser.add_argument(
        '--config',
        '-c',
        help='Specify config file for the telnetd server.',
        default='./ppp.conf'
    )
    parser.add_argument(
        '--pppd',
        help='Specify the path of pppd.',
        default='/usr/sbin/pppd'
    )
    args = parser.parse_args();
    pppdExec = args.pppd;

    #Test json format
    with open(args.config, 'r') as f:
        loginInfo=json.load(f);

    asyncio.run(main(args.host,args.port))