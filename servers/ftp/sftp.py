import logging
import asyncio
import aioftp
import asyncssh
from pathlib import PurePosixPath
from typing import Union, List, AsyncIterable, Any
from util import ServerGroup


class SFTPStat:
    def __init__(self,stat):
        self.st_mtime=stat.mtime
        self.st_atime=stat.atime
        self.st_mode=stat.permissions
        self.st_nlink=stat.nlink
        self.st_size=stat.size


class SFTPPathIO(aioftp.AbstractPathIO):
    def __init__(self,*,timeout=None,connection=None,state=None):
        self.logger=logging.getLogger(self.__class__.__name__)
        self._conn = connection
        self.__cwd=None

    @property
    def _sftp(self):
        try:
            return self._conn.user.sftp_client
        except Exception as e:
            self.logger.error(e,exc_info=True)
            raise aioftp.errors.PathIOError

    @property
    def _cwd(self):
        try:
            if self.__cwd is None:
                self.__cwd=self._conn.user.base_path
            return self.__cwd
        except Exception as e:
            self.logger.error(e,exc_info=True)
            raise aioftp.errors.PathIOError

    @_cwd.setter
    def _cwd(self,val):
        self.__cwd=val

    async def exists(self, path) -> bool:
        try:
            await self._sftp.lstat(str(self._cwd/path))
            return True
        except (asyncssh.sftp.SFTPNoSuchFile):
            return False
        except Exception as e:
            self.logger.error(e,exc_info=True)
            raise aioftp.errors.PathIOError

    async def is_dir(self, path) -> bool:
        try:
            stat = await self._sftp.lstat(str(self._cwd/path))
            return stat.type == asyncssh.sftp.FILEXFER_TYPE_DIRECTORY
        except (asyncssh.sftp.SFTPNoSuchFile):
            return False
        except Exception as e:
            self.logger.error(e,exc_info=True)
            raise aioftp.errors.PathIOError

    async def is_file(self, path) -> bool:
        try:
            stat = await self._sftp.lstat(str(self._cwd/path))
            return stat.type == asyncssh.sftp.FILEXFER_TYPE_REGULAR
        except (asyncssh.sftp.SFTPNoSuchFile):
            return False
        except Exception as e:
            self.logger.error(e,exc_info=True)
            raise aioftp.errors.PathIOError

    async def list(self, path) -> AsyncIterable[Any]:
        try:
            self._cwd=self._cwd/path
            for item in await self._sftp.listdir(self._cwd):
                if item!='.':
                    yield PurePosixPath(item)
        except Exception as e:
            self.logger.error(e,exc_info=True)
            raise aioftp.errors.PathIOError

    async def mkdir(self, path, *, parents: bool = False) -> None:
        try:
            full_path=str(self._cwd/path)
            if parents:
                await self._sftp.makedirs(full_path)
            else:
                await self._sftp.mkdir(full_path)
        except Exception as e:
            self.logger.error(e,exc_info=True)
            raise aioftp.errors.PathIOError

    async def rmdir(self, path) -> None:
        try:
            await self._sftp.rmdir(str(self._cwd/path))
        except asyncssh.sftp.SFTPNoSuchFile:
            raise aioftp.errors.PathIOError
        except Exception as e:
            self.logger.error(e,exc_info=True)
            raise aioftp.errors.PathIOError

    async def unlink(self, path) -> None:
        try:
            await self._sftp.unlink(str(self._cwd/path))
        except asyncssh.sftp.SFTPNoSuchFile:
            raise aioftp.errors.PathIOError
        except Exception as e:
            self.logger.error(e,exc_info=True)
            raise aioftp.errors.PathIOError

    async def rename(self, src, dst) -> None:
        try:
            await self._sftp.rename(str(self._cwd/src), str(self._cwd/dst))
        except asyncssh.sftp.SFTPNoSuchFile:
            raise aioftp.errors.PathIOError
        except Exception as e:
            self.logger.error(e,exc_info=True)
            raise aioftp.errors.PathIOError

    async def stat(self, path) -> Any:
        try:
            file_stat=await self._sftp.stat(str(self._cwd/path))
            return SFTPStat(file_stat)
        except asyncssh.sftp.SFTPNoSuchFile:
            raise aioftp.errors.PathIOError
        except Exception as e:
            self.logger.error(e,exc_info=True)
            raise aioftp.errors.PathIOError

    async def _open(self, path, mode: str = "rb"):
        mode_sftp="rb"
        if "a" in mode:
            mode_sftp="ab+"
        elif "w" in mode or "+" in mode:
            mode_sftp="wb+"
        try:
            return await self._sftp.open(str(self._cwd/path),mode_sftp)
        except asyncssh.sftp.SFTPNoSuchFile:
            raise aioftp.errors.PathIOError
        except Exception as e:
            self.logger.error(e,exc_info=True)
            raise aioftp.errors.PathIOError

    async def read(self, fp, size: int) -> bytes:
        return await fp.read(size)

    async def write(self, fp, data: bytes) -> int:
        return await fp.write(data)

    async def seek(self, fp, position: int) -> int:
        return await fp.seek(position)

    async def close(self, fp) -> None:
        await fp.close()


class SFTPUserManager(aioftp.AbstractUserManager):
    def __init__(self, sftp_host: str, sftp_port: int):
        self.logger=logging.getLogger(self.__class__.__name__)
        self._host = sftp_host
        self._port = sftp_port

    async def get_user(self, login: str) -> aioftp.User:
        stat=aioftp.AbstractUserManager.GetUserResponse.PASSWORD_REQUIRED
        user=aioftp.User(login=login, permissions=[
            aioftp.Permission("/",readable=True,writable=True)
        ])
        return stat,user,'Password Required'

    async def authenticate(self, user: aioftp.User, password: str) -> bool:
        try:
            conn = await asyncssh.connect(
                host=self._host,
                port=self._port,
                username=user.login,
                password=password,
                known_hosts=None
            )
            user.sftp_conn = conn
            user.sftp_client = await conn.start_sftp_client()
            base_path=await user.sftp_client.realpath('.')
            user.home_path='/'
            user.base_path=PurePosixPath(base_path)
            return True
        except asyncssh.misc.PermissionDenied:
            return False
        except Exception as e:
            self.logger.error(e,exc_info=True)
            return False

    async def notify_logout(self,user):
        if user is None:
            return
        try:
            if hasattr(user,'sftp_client'):
                await user.sftp_client.close()
        finally:
            if hasattr(user,'sftp_conn'):
                await user.sftp_conn.close()


class FTP2SFTPBridgeServerInstance(aioftp.Server):
    def __init__(self, config):
        self._config=config
        super().__init__(
            users=SFTPUserManager(
                sftp_host=self._config['sftp_host'],
                sftp_port=self._config.get('sftp_port',22)
            ),
            data_ports=range(self._config['pasv_port_start'],
                             self._config['pasv_port_end']+1),
            path_io_factory=SFTPPathIO,
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


class FTP2SFTPBridgeServer(ServerGroup):
    def __init__(self,config):
        super().__init__(config[self.__class__.__name__],
                         FTP2SFTPBridgeServerInstance)

