import asyncio
from util import Logger


class TCPServer(Logger):
    __server=None
    def __init__(self,port,*,host='0.0.0.0',max_conn=None):
        self.__port=port
        self.__host=host
        self.__max_conn=max_conn
        self.__conn=set()
        self.__lock=asyncio.Lock()
        self.__wait_close=asyncio.Event()

    async def __aenter__(self):
        self.__server=await asyncio.start_server(self.__handler,
            host=self.__host,port=self.__port,
            reuse_address=True,reuse_port=True)
        return self

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        await self.__wait_close.wait()
        self.__server.close()
        wait_tasks=[self.__server.wait_closed()]
        async with self.__lock:
            self.__max_conn=0
            for conn in self.__conn:
                conn.close()
                wait_tasks.append(conn.wait_closed())
        await asyncio.gather(*wait_tasks)

    async def __close_conn(self,writer):
        try:
            writer.close()
            await writer.wait_closed()
        except (ConnectionResetError,BrokenPipeError):
            pass
        except asyncio.TimeoutError:
            self.logger.warning('Close timed-out connection by force')
            writer.transport.abort()
        except Exception as e:
            self.logger.error(e,exc_info=True)
        finally:
            async with self.__lock:
                self.__conn.discard(writer)
    
    async def __handler(self,reader,writer):
        try:
            async with self.__lock:
                if self.__max_conn is None or len(self.__conn)<self.__max_conn:
                    self.__conn.add(writer)
                else:
                    return
            await self.handler(reader,writer)
        except (ConnectionResetError,BrokenPipeError,asyncio.TimeoutError) as e:
            self.logger.debug(e,exc_info=True)
        except Exception as e:
            self.logger.error(e,exc_info=True)
        finally:
            await self.__close_conn(writer)

    def close(self):
        self.__wait_close.set()

    async def handler(self,reader,writer):
        pass


class SingleUserConnManager(Logger):
    def __init__(self):
        self.__active_users_lock=asyncio.Lock()
        self.__active_users={}

    @staticmethod
    def __get_writer_id(writer):
        addr=writer.get_extra_info('peername')
        return f"{addr[0]}:{addr[1]}"

    async def login(self,username,writer):
        if username is None or writer is None:
            return
        writer_orig=None
        async with self.__active_users_lock:
            if username in self.__active_users:
                writer_orig=self.__active_users[username]
            self.__active_users[username]=writer
        if writer_orig is not None:
            self.logger.debug(f'{username} has existing conn {self.__class__.__get_writer_id(writer_orig)}')
            writer_orig.close()
            await writer_orig.wait_closed()
            self.logger.debug(f'{username} existing conn closed')

    async def logout(self,username,writer):
        if username is None or writer is None:
            return
        async with self.__active_users_lock:
            if username not in self.__active_users:
                return
            writer_del=self.__active_users[username]
            id_curr=self.__class__.__get_writer_id(writer)
            id_del=self.__class__.__get_writer_id(writer_del)
            if id_curr==id_del:
                del self.__active_users[username]
                self.logger.debug(f'Deleted {username} {id_curr}')
            else:
                self.logger.debug(f'{username} not deleted {id_del}!={id_curr}')

