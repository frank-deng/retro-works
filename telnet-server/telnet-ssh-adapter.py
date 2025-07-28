#!/usr/bin/env python3

import logging
import tomllib
import asyncio
import asyncssh
import signal
from util import Logger
from util import TCPServer
from util import LoginHandler


class SSHHandler(Logger):
    __password=None
    __conn=None
    __session=None
    __channel=None
    __tasks=None
    __buf_size=4096
    def __init__(self,reader,writer,config,password):
        self.__reader,self.__writer=reader,writer
        self.__config=config
        self.__password=password.decode()
        self.__loop=asyncio.get_running_loop()
        self.__queue=asyncio.Queue()
        self.logger.debug(config)

    async def __aenter__(self):
        try:
            self.__conn = await asyncssh.connect(
                host=self.__config['host'],
                port=self.__config['port'],
                username=self.__config['remote_username'],
                password=self.__password,
                known_hosts=None
            )
            self.__password=None
            self.__channel,self.__session=await self.__conn.create_session(
                asyncssh.SSHClientSession,
                term_type=self.__config.get('term',None),
                term_size=(80,24),
                encoding=None
            )
            self.__tasks=(
                asyncio.create_task(self.__ssh_to_tcp()),
                asyncio.create_task(self.__tcp_to_ssh())
            )
        except Exception:
            await self.__cleanup()
            raise

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        if self.__tasks is not None:
            await asyncio.wait(self.__tasks,return_when=asyncio.FIRST_COMPLETED)
        await self.__cleanup()

    async def __cleanup(self):
        try:
            if self.__tasks is not None:
                for task in self.__tasks:
                    if not task.done():
                        task.cancel()
                await asyncio.gather(*self.__tasks)
            if self.__conn is not None:
                self.__conn.close()
                await self.__conn.wait_closed()
        except Exception:
            raise

    def __ssh_read(self,data,_):
        try:
            if not data:
                self.__loop.call_soon(self.__queue.put_nowait,b"")
                return
            self.__queue.put_nowait(data)
        except asyncio.CancelledError:
            self.__queue.put_nowait(b"")
        except Exception as e:
            self.logger.error(e,exc_info=True)
            self.__queue.put_nowait(b"")

    async def __ssh_to_tcp(self):
        self.__session.data_received=self.__ssh_read
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

    async def __tcp_to_ssh(self):
        try:
            while True:
                data=await self.__reader.read(self.__buf_size)
                if not data:
                    break
                self.__channel.write(data)
        except (ConnectionResetError,asyncio.CancelledError):
            pass
        except Exception as e:
            self.__channel.close()
            await self.__channel.wait_closed()


class TelnetServer(TCPServer):
    def __init__(self,config):
        super().__init__(
            config.get('port',2333),
            host=config.get('host','0.0.0.0'),
            max_conn=config.get('max_connection',None)
        )
        self.__login_retry=config.get('login_retry',None)
        self.__login_timeout=config.get('login_timeout',None)
        self.__userinfo={}
        for item in config['servers']:
            username=item['username']
            if username in self.__userinfo:
                raise ValueError(f'Duplicated user {username}')
            if 'remote_username' not in item:
                item['remote_username']=username
            self.__userinfo[username]=item

    def __get_userinfo(self,username):
        if username is None:
            return None
        username=username.decode()
        return self.__userinfo.get(username,None)

    async def __login(self,reader,writer):
        login_handler=LoginHandler(reader,writer,
                                   retry=self.__login_retry,
                                   timeout=self.__login_timeout)
        while True:
            username,password=await login_handler.login()
            if username is None:
                return None,None
            userinfo=self.__get_userinfo(username)
            if userinfo is not None:
                return userinfo,password
            await login_handler.write(b'Login Failed.\r\n')
            await asyncio.sleep(3)

    async def handler(self,reader,writer):
        while True:
            userinfo,password=await self.__login(reader,writer)
            if userinfo is None:
                break
            try:
                async with SSHHandler(reader,writer,userinfo,password):
                    pass
            except asyncssh.misc.PermissionDenied:
                self.__writer.write(b'Login Failed.\r\n')
                await asyncio.sleep(3)
            except Exception as e:
                self.logger.error(e,exc_info=True)
		
async def main(config):
    try:
        async with TelnetServer(config) as server:
            loop = asyncio.get_event_loop()
            for s in (signal.SIGINT,signal.SIGTERM,signal.SIGQUIT):
                loop.add_signal_handler(s,server.close)
    except Exception as e:
        logging.getLogger(main.__name__).critical(e,exc_info=True)

if '__main__'==__name__:
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument(
        '--config',
        '-c',
        help='Specify config file for the PPP server.',
        default='ppp-manager.ini'
    )
    args=parser.parse_args();
    config=None
    with open(args.config, 'rb') as f:
        config=tomllib.load(f)
    log_level=config.get('log_level','INFO')
    logging.basicConfig(
        filename=config.get('log_file','telnet-ssh-adapter.log'),
        level=getattr(logging,log_level,logging.INFO)
    )
    try:
        asyncio.run(main(config))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.getLogger(main.__name__).critical(e,exc_info=True)

