import logging
import asyncio
import aioftp
import hashlib
from pathlib import PurePosixPath
from typing import Union, List, AsyncIterable, Any


class TermuxUserManager(aioftp.AbstractUserManager):
    def __init__(self, config):
        self._config=config

    async def get_user(self, login: str) -> aioftp.User:
        stat=aioftp.AbstractUserManager.GetUserResponse.PASSWORD_REQUIRED
        base_path=self._config.get('base_path',
                                   '/data/data/com.termux/files/home')
        user=aioftp.User(login=login,
            home_path='/',
            base_path=PurePosixPath(base_path),
            permissions=[aioftp.Permission("/",readable=True,writable=True)])
        return stat,user,'Password Required'

    async def authenticate(self, user: aioftp.User, password: str) -> bool:
        password_hash=hashlib.sha256(
            password.encode('iso8859-1',errors='ignore')).hexdigest()
        return self._config['password']==password_hash


class FTPTermuxServer(aioftp.Server):
    def __init__(self, config):
        self._config=config[self.__class__.__name__]
        super().__init__(
            users=TermuxUserManager(self._config),
            data_ports=range(self._config['pasv_port_start'],
                             self._config['pasv_port_end']+1),
            ipv4_pasv_forced_response_address=self._config.get('pasv_addr'),
            idle_timeout=self._config.get('idle_timeout',300),
            maximum_connections=self._config.get('max_connections',50),
            encoding=self._config.get('encoding','utf-8')
        )

    async def __aenter__(self):
        ftp_config=self._config
        await self.start(ftp_config.get('host','127.0.0.1'),
                         ftp_config.get('port',21))
        return self

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        await self.close()

