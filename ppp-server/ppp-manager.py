#!/usr/bin/env python3

import asyncio
import signal
import hashlib
import subprocess
import pty
import fcntl
import os
import configparser
import logging
import time
import uuid


class Logger:
    _logger = None

    @property
    def logger(self):
        if self._logger is None:
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger


class PPPApp(Logger):
    __master=None
    __slave=None
    __proc=None
    def __init__(self,config,reader,writer,*,userinfo):
        self.__reader,self.__writer=reader,writer
        self.__pppd_exec=config.get('pppd','exec',fallback='/usr/local/sbin/pppd')
        self.__pppd_options=config.get('pppd','options',fallback='').split()
        self.__ipaddr=userinfo[0]
        self.logger.debug(' '.join(self.__pppd_options))

    async def __aenter__(self):
        return self

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        if self.__slave is not None:
            os.close(self.__slave)
        if self.__master is not None:
            os.close(self.__master)
        await self.__writer.drain()
        if self.__proc is not None:
            try:
                await asyncio.wait_for(self.__proc.communicate(),timeout=10)
            except asyncio.TimeoutError:
                self.__proc.kill()

    def __proc_args(self,args,**kwargs):
        res=[]
        for item in args:
            item_new=item
            for key in kwargs:
                item_new=item_new.replace(f'@{key}@',kwargs[key])
            res.append(item_new)
        return res

    async def run_forever(self):
        self.__master,self.__slave=pty.openpty()
        fcntl.fcntl(self.__master, fcntl.F_SETFL, fcntl.fcntl(self.__master, fcntl.F_GETFL) | os.O_NONBLOCK)
        fcntl.fcntl(self.__slave, fcntl.F_SETFL, fcntl.fcntl(self.__slave, fcntl.F_GETFL) | os.O_NONBLOCK)
        args=self.__proc_args(self.__pppd_options,
                              pty="/proc/%d/fd/%d"%(os.getpid(),self.__slave),
                              ip_addr=self.__ipaddr)
        self.logger.debug(' '.join(args))
        self.__proc=await asyncio.create_subprocess_exec(
            *[self.__pppd_exec,]+args,
            bufsize=0,
            start_new_session=True,
            stdin=self.__slave,
            stdout=self.__slave,
            stderr=self.__slave)
        self.__writer.write(b'Success\r\n')
        await self.__writer.drain()
        while True:
            try:
                self.__writer.write(os.read(self.__master,1024))
            except BlockingIOError:
                pass
            try:
                content=await asyncio.wait_for(self.__reader.read(1024),timeout=1)
                if not content:
                    raise BrokenPipeError
                os.write(self.__master, content)
            except (asyncio.TimeoutError,BlockingIOError):
                pass


class PPPConnection(Logger):
    __username=None
    __task=None
    __retry=0
    def __init__(self,config,reader,writer,*,onlogin,onlogout):
        self.__config=config
        self.__id=uuid.uuid4()
        self.__login_timeout=config.getint('server','login_timeout',fallback=120)
        self.__max_retry=config.getint('server','max_retry',fallback=3)
        self.__reader,self.__writer=reader,writer
        self.__timestamp=time.time()
        self.__onlogin=onlogin
        self.__onlogout=onlogout

    async def __readchar(self):
        running=True
        char=0
        while running:
            running=False
            try:
                char=await asyncio.wait_for(self.__reader.read(1),1)
            except asyncio.TimeoutError:
                running=True
            if time.time() - self.__timestamp > self.__login_timeout:
                raise asyncio.TimeoutError
        char=int.from_bytes(char,'little')
        if 0==char:
            raise BrokenPipeError
        return char

    async def __readline(self,echo=True,max_len=1024):
        reader,writer=self.__reader,self.__writer
        res=b''
        running=True
        while running:
            val=await self.__readchar()
            if 0x08==val and len(res)>0: #Backspace
                res=res[:-1]
                if(echo):
                    writer.write(b'\x08 \x08')
                    await writer.drain()
            elif val in (0x0d,0x0a): #Finished
                running=False
                writer.write(b'\r\n')
                await writer.drain()
            elif val>=0x20 and val<=0x7e and len(res)<max_len:
                res+=val.to_bytes(1,'little')
                if echo:
                    writer.write(val.to_bytes(1,'little'))
                    await writer.drain()
        # Ignore input after Enter as much as possible
        try:
            await asyncio.wait_for(reader.read(max_len), timeout=0.01)
        except asyncio.TimeoutError:
            pass
        return res

    async def __login(self):
        reader,writer=self.__reader,self.__writer
        self.__username=None
        writer.write(b'\r\nLogin:')
        await writer.drain()
        username=await self.__readline(True,80)
        if not username:
            return None
        writer.write(b'Password:')
        await writer.drain()
        password=await self.__readline(False,80)
        username=username.decode('UTF-8')
        password=hashlib.sha256(password).hexdigest();
        userinfo=await self.__onlogin(self,username,password)
        if userinfo is not None:
            self.__username=username
            return userinfo
        writer.write(b'Login Failed.\r\n')
        await asyncio.gather(writer.drain(),asyncio.sleep(3))
        self.__retry+=1
        if self.__retry>=self.__max_retry:
            raise asyncio.CancelledError
        return None
    
    async def __run(self):
        try:
            userinfo=None
            while userinfo is None:
                userinfo=await self.__login()
            async with PPPApp(self.__config,self.__reader,self.__writer,userinfo=userinfo) as app:
                await app.run_forever()
        except (asyncio.CancelledError,asyncio.TimeoutError,ConnectionResetError,BrokenPipeError) as e:
            self.logger.debug(f'Connection closed {e}')
        except Exception as e:
            self.logger.error(e,exc_info=True)
        finally:
            try:
                if not self.__writer.is_closing():
                    self.__writer.close()
                    await self.__writer.wait_closed()
                await self.__onlogout(self)
            except Exception as e:
                self.logger.error(e,exc_info=True)

    async def __aenter__(self):
        try:
            self.__task=asyncio.create_task(self.__run())
        except Exception as e:
            self.logger.error(e,exc_info=True)

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        if self.__task is not None:
            await self.__task

    @property
    def username(self):
        return self.__username

    @property
    def conn_id(self):
        return self.__id

    async def close(self):
        if self.__task is not None:
            self.__task.cancel()
            await self.__task


class PPPUserManager(Logger):
    def __init__(self,config):
        self.__userlist_file=config.get('server','userlist')
        self.__passwd={}
        self.__userinfo={}
        self.__conn_info_lock=asyncio.Lock()
        self.__conn_user={}
        self.__conn_id={}

    async def __aenter__(self):
        with open(self.__userlist_file,'r',encoding='utf-8') as fp:
            for line in fp:
                line_data=line.strip().split('|')
                username=line_data[0]
                self.__passwd[username]=line_data[1]
                self.__userinfo[username]=tuple(line_data[2:])
                self.logger.debug(f'{line_data}')

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        self.__passwd={}
        self.__userinfo={}
        self.__conn_user={}
        self.__conn_id={}

    async def _login_handler(self,conn,user,passwd):
        if user is None or passwd is None:
            return None
        if user not in self.__passwd or passwd!=self.__passwd[user]:
            self.logger.debug(f'{passwd} {self.__passwd[user]}')
            return None
        conn_orig=None
        async with self.__conn_info_lock:
            conn_orig=self.__conn_user.get(user,None)
            if conn_orig is not None:
                del self.__conn_id[conn_orig.conn_id]
            self.__conn_user[user]=conn
            self.__conn_id[conn.conn_id]=conn
            self.logger.debug(f'Applied curr conn for {user}')
        if conn_orig is not None:
            self.logger.debug(f'Found existing conn for {user}')
            await conn_orig.close()
        self.logger.debug(f'{self.__userinfo[user]}')
        return self.__userinfo[user]

    async def _logout_handler(self,conn):
        async with self.__conn_info_lock:
            if conn.conn_id in self.__conn_id:
                self.logger.debug(f'Delete conn for {conn.username} by id')
                del self.__conn_id[conn.conn_id]
            conn_by_user=None
            username=conn.username
            if username is not None and username in self.__conn_user:
                conn_by_user=self.__conn_user.get(username,None)
            if conn_by_user is not None and conn_by_user.conn_id==conn.conn_id:
                self.logger.debug(f'Delete conn for {conn.username} by username')
                del self.__conn_user[username]


class PPPServer(PPPUserManager):
    __server=None
    __shutdown=False
    def __init__(self,config):
        super().__init__(config)
        self.__config=config
        self.__host=config.get('server','host',fallback='0.0.0.0')
        self.__port=config.getint('server','port',fallback=2345)
        self.__conn=set()
        self.__conn_lock=asyncio.Lock()

    async def __aenter__(self):
        await super().__aenter__()
        self.__server=await asyncio.start_server(self.__handler,
            host=self.__host,port=self.__port,
            reuse_address=True,reuse_port=True)
        return self

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        await self.__server.wait_closed()
        await super().__aexit__(exc_type,exc_val,exc_tb)
        self.logger.debug('close server finish')

    async def serve_forever(self):
        if self.__server is None:
            raise RuntimeError('Server not initialized')
        try:
            async with self.__server:
                await self.__server.serve_forever()
        except asyncio.CancelledError:
            pass

    async def shutdown(self):
        try:
            if self.__shutdown:
                return
            self.__shutdown=True
            self.logger.debug('start shutdown')
            if self.__server is not None:
                self.__server.close()
            conn_all=set()
            async with self.__conn_lock:
                conn_all=self.__conn.copy()
            await asyncio.gather(*[conn.close() for conn in conn_all])
            self.logger.debug('close all connection finish')
        except Exception as e:
            self.logger.error(e,exc_info=True)

    async def __handler(self,reader,writer):
        conn=None
        if self.__shutdown:
            return
        try:
            conn=PPPConnection(self.__config,reader,writer,
                               onlogin=self._login_handler,
                               onlogout=self._logout_handler)
            async with conn:
                async with self.__conn_lock:
                    self.__conn.add(conn)
                    self.logger.debug(f'Start conn. Connections: {len(self.__conn)}')
        except Exception as e:
            self.logger.error(e,exc_info=True)
        finally:
            async with self.__conn_lock:
                self.__conn.discard(conn)
                self.logger.debug(f'End conn. Connections: {len(self.__conn)}')

		
async def main(config):
    try:
        async with PPPServer(config) as server:
            loop = asyncio.get_event_loop()
            for s in (signal.SIGINT,signal.SIGTERM,signal.SIGQUIT):
                loop.add_signal_handler(s,lambda:asyncio.create_task(server.shutdown()))
            await server.serve_forever()
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
    config=configparser.ConfigParser()
    config.read(args.config)
    log_level=config.get('server','log_level',fallback='INFO')
    logging.basicConfig(
        filename=config.get('server','log_file',fallback='ppp-manager.log'),
        level=getattr(logging,log_level,logging.INFO)
    )
    try:
        asyncio.run(main(config))
    except Exception as e:
        logging.getLogger(main.__name__).critical(e,exc_info=True)
