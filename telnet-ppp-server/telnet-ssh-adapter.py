#!/usr/bin/env python3

import asyncio,signal,paramiko,socket,json
from traceback import print_exc

login_timeout=120
loginInfo={}

async def read_line(reader,writer,echo=True,max_len=1024):
    res=b''
    running=True
    while running:
        char=await asyncio.wait_for(reader.read(1), timeout=login_timeout)
        val=int.from_bytes(char,'little')
        if 0x08==val and len(res)>0: #Backspace
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
    username=await read_line(reader,writer,echo=True,max_len=80)
    if not username:
        return
    writer.write(b'Password:')
    password=await read_line(reader,writer,echo=False,max_len=80)
    username=username.decode('UTF-8')
    password=password.decode('UTF-8')
    __loginInfo=loginInfo.get(username)
    if (__loginInfo is None):
        writer.write(b'Invalid Login.\r\n')
        await writer.drain()
        return
    trans=None
    channel=None
    try:
        trans=paramiko.Transport((__loginInfo.get('addr','127.0.0.1'),__loginInfo.get('port',22),))
        trans.start_client()
        trans.auth_password(__loginInfo.get('user',username), password)
        channel=trans.open_session()
        channel.get_pty(
            __loginInfo.get('term','ansi'),
            __loginInfo.get('cols',80),
            __loginInfo.get('lines',24)
        )
        channel.invoke_shell()
        channel.setblocking(0)
    except Exception as e:
        print_exc()
        writer.write(b'Invalid Login.\r\n')
        await writer.drain()
        trans.close()
        return
    try:
        socket_closed=False
        while trans.is_active() and channel.active and (not channel.closed) and not socket_closed:
            trans.send_ignore()
            try:
                content=channel.recv(1024)
                if content:
                    writer.write(content)
            except socket.timeout:
                pass
            try:
                content=await asyncio.wait_for(reader.read(1024), timeout=0.01)
                if not content:
                    socket_closed=True
                else:
                    channel.send(content);
            except asyncio.TimeoutError:
                pass
            except socket.timeout:
                pass
    except Exception as e:
        print_exc()
    finally:
        channel.close()
        trans.close()
    writer.write(b'\r\nSession closed.\r\n')
    await writer.drain()

async def service_handler(reader,writer):
    try:
        while True:
            await service_main(reader,writer)
    except asyncio.TimeoutError:
        writer.write(b'\r\n\r\nTimeout!!\r\n')
    except ConnectionResetError:
        pass
    finally:
        writer.close()
        await writer.wait_closed()
		
def exception_handler(loop, context):
    exception = context['exception']
    if isinstance(exception,BrokenPipeError):
        return
    message=context['message']
    print(f'Task failed, msg={message}, exception={exception}')
		
async def main(host,port):
    server=await asyncio.start_server(service_handler,
        host=host,port=port,reuse_address=True,reuse_port=True)
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(exception_handler)
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
        default='./ssh.conf'
    )
    args = parser.parse_args()

    #Test json format
    with open(args.config, 'r') as f:
        loginInfo=json.load(f)
    
    asyncio.run(main(args.host,args.port))