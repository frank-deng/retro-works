import asyncio
import logging
import time
import os
import pty

class Logger:
    _logger=None

    @property
    def logger(self):
        if self._logger is None:
            self._logger=logging.getLogger(self.__class__.__name__)
        return self._logger


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

    async def __add_conn(self,writer):
        async with self.__lock:
            if self.__max_conn is None or len(self.__conn)<self.__max_conn:
                self.__conn.add(writer)
                return True
        return False

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
            if await self.__add_conn(writer):
                await self.handler(reader,writer)
        except (ConnectionResetError,BrokenPipeError):
            pass
        except Exception as e:
            self.logger.error(e,exc_info=True)
        finally:
            await self.__close_conn(writer)

    def close(self):
        self.__wait_close.set()

    async def handler(self,reader,writer):
        pass


class ConnectionHandler(Logger):
    __timeout=None
    __timestamp=None
    def __init__(self,reader,writer):
        self.__reader,self.__writer=reader,writer

    def __check_timeout(self):
        if self.__timeout is None or self.__timestamp is None:
            return
        elif time.time() - self.__timestamp > self.__timeout:
            raise asyncio.TimeoutError

    def set_timeout(self,timeout):
        self.__timeout=timeout
        if timeout is None:
            self.__timestamp=None
        else:
            self.__timestamp=time.time()

    async def read(self,size,timeout=None):
        data=None
        if timeout is not None:
            try:
                data=await asyncio.wait_for(self.__reader.read(size),
                                            timeout=timeout)
            except asyncio.TimeoutError:
                pass
        else:
            data=await self.__reader.read(size)
        self.__check_timeout()
        return data 

    async def write(self,data):
        self.__writer.write(data)
        await self.__writer.drain()
        self.__check_timeout()


class ReadlineHandler(ConnectionHandler):
    __echo=True
    __len=0
    def __init__(self,reader,writer,size=1024):
        super().__init__(reader,writer)
        self.__inp=bytearray(size)
        self.__size=size

    async def __read_char(self):
        char=None
        while char is None:
            char=await self.read(1,1)
        return char

    async def __handle_backspace(self):
        if self.__len<=0:
            return
        self.__len-=1
        if self.__echo:
            await self.write(b'\x08 \x08')

    async def __handle_char(self,char):
        val=int.from_bytes(char,'little')
        if val>=0x20 and val<=0x7e and self.__len<self.__size:
            self.__inp[self.__len]=val
            self.__len+=1
            if self.__echo:
                await self.write(char)

    async def readline(self,*,echo=True):
        self.__echo=echo
        self.__len=0
        while True:
            char=await self.__read_char()
            if char==b'': #Disconnected
                self.__len=None
                break
            elif char in (b'\x0d',b'\x0a'): #Finished
                await self.write(b'\r\n')
                break
            elif b'\x08'==char: #Backspace
                await self.__handle_backspace()
            else:
                await self.__handle_char(char)
        res=None
        if self.__len is not None:
            # Ignore input after Enter as much as possible
            res=bytes(self.__inp[:self.__len])
            await self.read(1000,0.01)
        return res


class LoginHandler(ReadlineHandler):
    __retry=None
    def __init__(self,reader,writer,*,retry=None,timeout=None):
        super().__init__(reader,writer,70)
        self.__retry=retry
        self.set_timeout(timeout)

    def __check_retry(self):
        if self.__retry is None:
            return True
        if self.__retry<=0:
            return False
        self.__retry-=1
        return True

    async def __get_username(self):
        username=b''
        while username==b'':
            await self.write(b'\r\nLogin:')
            username=await self.readline(echo=True)
        return username

    async def login(self):
        if not self.__check_retry():
            return None,None
        username=await self.__get_username()
        if username is None:
            return None,None
        await self.write(b'Password:')
        password=await self.readline(echo=False)
        if password is None:
            return None,None
        return username,password


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


class ProcessHandler(Logger):
    __buf_size=4096
    __proc=None
    __master_fd=None
    __slave_fd=None
    __pty_reader=None
    __tasks=None
    def __init__(self,reader,writer,*,buf_size=4096):
        self.__reader,self.__writer=reader,writer
        self.__buf_size=buf_size
        self.__loop=asyncio.get_running_loop()
        self.__queue=asyncio.Queue()

    async def __aenter__(self):
        try:
            self.__master_fd,self.__slave_fd=pty.openpty()
            self.__proc=await self.create_subprocess_exec(self.__slave_fd)
            os.set_blocking(self.__master_fd,False)
            self.__tasks=(
                asyncio.create_task(self.__pty_to_tcp()),
                asyncio.create_task(self.__tcp_to_pty())
            )
        except Exception as e:
            await self.__cleanup()
            raise
        return self

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        if self.__tasks is not None:
            await asyncio.wait(self.__tasks,return_when=asyncio.FIRST_COMPLETED)
        await self.__cleanup()

    def __fd_ready(self):
        try:
            data=os.read(self.__master_fd,self.__buf_size)
            if not data:
                self.__loop.call_soon(self.__queue.put_nowait,b"")
                return
            self.__queue.put_nowait(data)
        except (OSError,asyncio.CancelledError):
            self.__queue.put_nowait(b"")

    async def __pty_to_tcp(self):
        self.__loop.add_reader(self.__master_fd,self.__fd_ready)
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
        finally:
            self.__loop.remove_reader(self.__master_fd)

    async def __write_fd(self,data):
        n=None
        while data:
            try:
                n=os.write(self.__master_fd,data)
                data=data[n:]
            except BlockingIOError:
                self.logger.debug(f'Partial data written {n}/{len(data)}')
                await asyncio.sleep(0.01)

    async def __tcp_to_pty(self):
        try:
            while True:
                data=await self.__reader.read(self.__buf_size)
                if not data:
                    break
                await self.__write_fd(data)
        except (ConnectionResetError,OSError,asyncio.CancelledError):
            pass
        except Exception as e:
            self.logger.error(e,exc_info=True)

    async def __cleanup(self):
        try:
            if self.__tasks is not None:
                for task in self.__tasks:
                    if not task.done():
                        task.cancel()
                await asyncio.gather(*self.__tasks)
        except Exception as e:
            self.logger.error(e,exc_info=True)
        finally:
            self.__close_fd(self.__master_fd)
            self.__close_fd(self.__slave_fd)
            await self.__stop_proc()

    def __close_fd(self,fd):
        try:
            if fd is not None:
                os.close(fd)
        except Exception as e:
            self.logger.error(e,exc_info=True)

    async def __stop_proc(self):
        try:
            if self.__proc is None or self.__proc.returncode is not None:
                return
            await asyncio.wait_for(self.__proc.communicate(),timeout=10)
        except asyncio.TimeoutError:
            self.__proc.kill()
            await asyncio.wait_for(self.__proc.wait(),timeout=10)
        finally:
            self.__proc=None

    async def create_subprocess_exec(self,slave_fd):
        pass

