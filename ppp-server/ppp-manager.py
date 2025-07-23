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
import csv
from io import StringIO

from util import Logger
from util import TCPServer
from util import LoginHandler
from util import SingleUserConnManager

class PPPApp(Logger):
    __master=None
    __slave=None
    __proc=None

    @staticmethod
    def __proc_args(args,**kwargs):
        res=[]
        for item in args:
            item_new=item
            for key in kwargs:
                item_new=item_new.replace(f'@{key}@',kwargs[key])
            res.append(item_new)
        return res

    def __init__(self,config,reader,writer,*,userinfo,bufsize=1024):
        self.__reader,self.__writer=reader,writer
        self.__pppd_exec=config.get('pppd','exec',fallback='/usr/local/sbin/pppd')
        self.__pppd_options=config.get('pppd','options',fallback='').split()
        self.__ipaddr=userinfo['ip_addr']
        self.__bufsize=bufsize
        self.logger.debug(' '.join(self.__pppd_options))

    async def __aenter__(self):
        self.__master,self.__slave=pty.openpty()
        fcntl.fcntl(self.__master, fcntl.F_SETFL, fcntl.fcntl(self.__master, fcntl.F_GETFL) | os.O_NONBLOCK)
        fcntl.fcntl(self.__slave, fcntl.F_SETFL, fcntl.fcntl(self.__slave, fcntl.F_GETFL) | os.O_NONBLOCK)
        args=self.__class__.__proc_args(self.__pppd_options,
            pty="/proc/%d/fd/%d"%(os.getpid(),self.__slave),
            ip_addr=self.__ipaddr)
        self.logger.debug('$'.join(args))
        self.__proc=await asyncio.create_subprocess_exec(
            *[self.__pppd_exec,]+args,
            bufsize=0,
            start_new_session=True,
            stdin=self.__slave,
            stdout=self.__slave,
            stderr=self.__slave)
        self.logger.debug('pppd started')
        return self

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        if self.__slave is not None:
            os.close(self.__slave)
        if self.__master is not None:
            os.close(self.__master)
        await self.__writer.drain()
        if self.__proc is not None and self.__proc.returncode is None:
            try:
                await asyncio.wait_for(self.__proc.communicate(),timeout=10)
                self.logger.debug('pppd stopped normally')
            except asyncio.TimeoutError:
                self.__proc.kill()
                await asyncio.wait_for(self.__proc.wait(),timeout=10)
            finally:
                self.__proc=None
        await asyncio.sleep(1)
        self.logger.debug('pppd stopped')

    async def run_forever(self):
        while True:
            try:
                self.__writer.write(os.read(self.__master,self.__bufsize))
                await self.__writer.drain()
            except BlockingIOError:
                pass
            try:
                content=await asyncio.wait_for(self.__reader.read(self.__bufsize),timeout=1)
                if not content:
                    break
                os.write(self.__master, content)
            except (asyncio.TimeoutError,BlockingIOError):
                pass


class PPPUserManager(SingleUserConnManager):
    def __init__(self,config):
        super().__init__()
        self.__passwd={}
        self.__userinfo={}
        users=set()
        for key in config['users']:
            if key in config['DEFAULT']:
                continue
            username,item=key.split('.')
            users.add(username)
            if item=='password':
                self.__passwd[username]=config['users'][key]
            elif item=='ip_addr':
                self.__userinfo[username]={'ip_addr':config['users'][key]}
        for user in users:
            if user not in self.__passwd or user not in self.__userinfo:
                raise ValueError(f'Incomplete data for user {user}')
            self.logger.debug(f'{user} {self.__passwd[user]} {self.__userinfo[user]}')

    async def login(self,username,password,writer):
        if username is None or password is None or self.__passwd.get(username,'')!=password:
            return None
        await super().login(username,writer)
        return self.__userinfo[username]


class PPPServer(TCPServer,PPPUserManager):
    def __init__(self,config):
        self.__config=config
        host=config.get('server','host',fallback='0.0.0.0')
        port=config.getint('server','port',fallback=2345)
        max_conn=config.getint('server','max_connection',fallback=None)
        TCPServer.__init__(self,port,host=host,max_conn=max_conn)
        PPPUserManager.__init__(self,config)
        self.__login_retry=config.getint('server','login_retry',fallback=None)
        self.__login_timeout=config.getint('server','login_timeout',fallback=None)

    async def handler(self,reader,writer):
        username,userinfo=None,None
        try:
            login_handler=LoginHandler(reader,writer,
                                       retry=self.__login_retry,
                                       timeout=self.__login_timeout)
            while True:
                username,password=await login_handler.login()
                if username is None:
                    return
                userinfo=await self.login(username,password,writer)
                if userinfo is not None:
                    break
                else:
                    await login_handler.write(b'Login Failed.\r\n')
                    asyncio.sleep(3)
            await login_handler.write(b'Login Succeed.\r\n')
            async with PPPApp(self.__config,reader,writer,userinfo=userinfo) as app:
                await app.run_forever()
        finally:
            await self.logout(username,writer)


class Initializer(Logger):
    __dns_task=None
    def __init__(self,config):
        self.__init_cmds=[
            ('sysctl','-w','net.ipv4.ip_forward=1'),
            ('iptables','-t','nat','-A','POSTROUTING','-s',
                config.get('pppd','ppp_client_subnet'),'-j','MASQUERADE'),
        ]
        reader=csv.reader(
            StringIO(config.get('pppd','routes',fallback='')),
            delimiter=' ',skipinitialspace=True)
        for row in reader:
            self.__init_cmds.append(tuple(['iptables']+row))

        self.__dnsmasq_cmd=[
            config.get('dns','dnsmasq',fallback='dnsmasq'),
            '--keep-in-foreground','--pid-file=','--no-resolv',
            '--no-hosts','--bind-interfaces'
        ]
        dnsmasq_key_blacklist={'local_ip','router_ip','dnsmasq','pid-file',
                               'no-resolv','no-hosts','bind-interfaces'}
        for key in config['dns']:
            if key in dnsmasq_key_blacklist:
                continue
            val=config['dns'][key]
            if not val:
                self.__dnsmasq_cmd.append(f'--{key}')
                continue
            for v in val.split('\n'):
                v=v.strip()
                self.__dnsmasq_cmd.append(f'--{key}={v}')
        self.logger.debug(f'dnsmasq cmd: {" ".join(self.__dnsmasq_cmd)}')
        self.__local_ip=config.get('server','local_ip')

    async def __run_cmd(self,cmd,*,timeout=None):
        cmd_str=" ".join(cmd)
        proc=None
        try:
            proc=await asyncio.create_subprocess_exec(*cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
            stdout,stderr=None,None
            if timeout is None:
                stdout,stderr=await proc.communicate()
            else:
                stdout,stderr=await asyncio.wait_for(proc.communicate(),
                                                     timeout=timeout)
            stdout,stderr,retcode=stdout.decode(),stderr.decode(),proc.returncode
            proc=None
            self.logger.debug(f'[{retcode}]{cmd_str}\n{stderr}\n---\n{stdout}')
            return stdout,stderr,retcode
        except asyncio.TimeoutError:
            self.logger.error(f'Timeout:{cmd_str}')
            return None,None,None
        except FileNotFoundError as e:
            self.logger.error(f'FileNotFound:{cmd_str}')
            return None,None,None
        except Exception as e:
            self.logger.error(f'{e}:{cmd_str}',exc_info=True)
            return None,None,None
        finally:
            if proc is not None and proc.returncode is None:
                proc.kill()
                await proc.wait()

    async def __task_dnsmasq(self):
        proc=None
        try:
            times=5
            ip_ready=False
            while not ip_ready and times>0:
                stdout,_,_=await self.__run_cmd(['ifconfig','-a'],timeout=10)
                if stdout and f'inet addr:{self.__local_ip}' in stdout:
                    ip_ready=True
                    break
                times-=1
                await asyncio.sleep(1)
            if not ip_ready:
                self.logger.error(f'IP {self.__local_ip} not ready')
                return
            proc=await asyncio.create_subprocess_exec(*self.__dnsmasq_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
            stdout,stderr=await proc.communicate()
            stdout,stderr,retcode=stdout.decode(),stderr.decode(),proc.returncode
            self.logger.error(f'Failed to start dnsmasq, ret:{retcode}\n{stderr}\n---\n{stdout}')
        except asyncio.CancelledError:
            pass
        except Exception as e:
            self.logger.error(e,exc_info=True)
        finally:
            if proc is not None and proc.returncode is None:
                proc.kill()
                await proc.wait()

    async def __aenter__(self):
        try:
            self.__dns_task=asyncio.create_task(self.__task_dnsmasq())
            for cmd in self.__init_cmds:
                await self.__run_cmd(cmd,timeout=10)
        except Exception as e:
            self.logger.error(e,exc_info=True)
            if self.__dns_task is not None:
                self.__dns_task.cancel()
                await self.__dns_task
                self.__dns_task=None
        return self

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        if self.__dns_task is not None:
            self.__dns_task.cancel()
            await self.__dns_task


async def main(config):
    try:
        async with Initializer(config) as _:
            async with PPPServer(config) as server:
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
    config=configparser.ConfigParser()
    config.read(args.config)
    log_level=config.get('server','log_level',fallback='INFO')
    logging.basicConfig(
        filename=config.get('server','log_file',fallback='ppp-manager.log'),
        level=getattr(logging,log_level,logging.INFO)
    )
    try:
        asyncio.run(main(config))
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.getLogger(main.__name__).critical(e,exc_info=True)

