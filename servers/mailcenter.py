import asyncio
import sys
import re
import hashlib
import aiosqlite
import time
import aiosqlite
from aiosqlitepool import SQLiteConnectionPool
from util import Logger
from util import load_module


async def sql_insert_single(conn,table,data:dict):
    columns=list(data.keys())
    cols_sql=','.join(columns)
    placeholders=','.join(['?'] * len(columns))
    values=tuple(data[col] for col in columns)
    sql=f'INSERT INTO {table} ({cols_sql}) VALUES ({placeholders})'
    return await conn.execute(sql,values)


async def sql_insert_multi(conn,table,data:list):
    columns=list(data[0].keys())
    cols_sql=','.join(columns)
    placeholders=','.join(['?'] * len(columns))
    values=[tuple(item[col] for col in columns) for item in data]
    sql=f'INSERT INTO {table} ({cols_sql}) VALUES ({placeholders})'
    return await conn.executemany(sql,values)


class MailUserRobot(Logger):
    def __init__(self,mailCenter,config):
        self._config=config
        self._task=None
        self._queue=asyncio.Queue()
        self._MailCenter=mailCenter
        self._uid=config['uid']

    async def __aenter__(self):
        self._task=asyncio.create_task(self._task_main())

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        if self._task is not None:
            self._task.cancel()
            await self._task

    async def _task_main(self):
        while True:
            try:
                email_id=await self._queue.get()
            except asyncio.CancelledError:
                break
            try:
                await self._handler(email_id)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(e,exc_info=True)
            finally:
                self._queue.task_done()

    async def append(self,data):
        await self._queue.put(data)

    async def _get_user_type(self,uid):
        res='user'
        if self._MailCenter.is_robot(uid):
            res='assistant'
        return res

    def _get_conversation(self,email_list):
        last_user_type=None
        res=[]
        for email in reversed(email_list):
            uid,subject,body=email['from_uid'],email['subject'],email['body']
            if re.match(r'^(Re:|Fwd:)',subject,re.IGNORECASE):
                subject=''
            else:
                subject+='\n'
            user_type=self._get_user_type(uid)
            if last_user_type is None or user_type!=last_user_type:
                last_user_type=user_type
                res.append(f'{subject}{body}')
            else:
                res[-1]+='\n'+f'{subject}{body}'
        return res

    async def _handler(self,email_id):
        pass


class MailCenterInstance(Logger):
    _setup_script="""
CREATE TABLE IF NOT EXISTS email_rel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id INTEGER NOT NULL,
    email_id_rel INTEGER NOT NULL
) STRICT;

CREATE TABLE IF NOT EXISTS email (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_uid INTEGER NOT NULL,
    sent_time INTEGER,
    subject TEXT,
    body TEXT,
    status INTEGER NOT NULL
) STRICT;

CREATE TABLE IF NOT EXISTS recipient (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id INTEGER NOT NULL,
    uid INTEGER NOT NULL,
    type INTEGER NOT NULL,
    status INTEGER NOT NULL
) STRICT;
"""
    def __init__(self,config):
        self._config=config
        self.pagesize=config['mail'].get('pagesize',30)
        self._host=config['mail']['host']
        self._load_users(config['mail']['users'])
        self._pool=SQLiteConnectionPool(connection_factory=self._create_conn)

    def _load_users(self,users):
        self._users={}
        self._users_by_name={}
        self._user_login={}
        self._robot={}
        for item in users:
            uid=item['uid']
            self._users[uid]=item
            self._users_by_name[item['username']]=item
            if 'password' in item:
                self._user_login[item['username']]=item
            elif 'module' in item:
                self._robot[uid]=load_module(item['module'])(self,item)

    async def _create_conn(self)->aiosqlite.Connection:
        config_db=self._config['mail']['db']
        conn=await aiosqlite.connect(config_db['db_file'])
        conn.row_factory=aiosqlite.Row
        busy_timeout=config_db.get('busy_timeout',5000)
        if not isinstance(busy_timeout,int):
            raise ValueError('busy_timeout must be int')
        cache_size=config_db.get('cache_size',8000)
        if not isinstance(cache_size,int):
            raise ValueError('cache_size must be int')
        await conn.execute("PRAGMA journal_mode=WAL;")
        await conn.execute(f"PRAGMA busy_timeout={busy_timeout};")
        await conn.execute(f"PRAGMA cache_size={cache_size};")
        await conn.execute("PRAGMA foreign_keys=ON;")
        await conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    async def is_robot(self,uid):
        return uid in self._robot

    async def auth(self,username,password):
        if not username or not password or username not in self._user_login:
            return None
        user=self._user_login[username]
        password_hash=hashlib.sha256(password.encode('iso8859-1',errors='ignore')).hexdigest()
        if user['password']!=password_hash:
            return None
        return user['uid']

    async def start(self):
        async with self._pool.connection() as conn:
            await conn.executescript(self._setup_script)
            await conn.commit()
        await asyncio.gather(*[bot.__aenter__() \
            for bot in self._robot.values()])

    async def stop(self):
        try:
            await asyncio.gather(*[bot.__aexit__(*sys.exc_info()) \
                for bot in self._robot.values()])
        except Exception as e:
            self.logger.error(e,exc_info=True)
        await self._pool.close()

    async def get_uid_from_addr(self,addr):
        items=addr.strip().split('@')
        if len(items)!=2:
            return None
        user,host=items[0],items[1]
        if host!=self._host or user not in self._users_by_name:
            return None
        return self._users_by_name[user]['uid']

    async def get_addr_from_uid(self,uid):
        if uid not in self._users:
            return None
        return self._users[uid]['username']+'@'+self._host

    async def send(self,from_uid,to_list,cc_list,subject,body,
                   prev_email_id=None):
        email_id=None
        async with self._pool.connection() as conn:
            try:
                email_list=[]
                if prev_email_id:
                    cursor=await conn.execute(
                        "SELECT email_id_rel from email_rel WHERE email_id=?",
                        (prev_email_id,))
                    email_list=[item['email_id_rel'] for item in await cursor.fetchall()]
                    email_list.append(prev_email_id)
                email_id=(await sql_insert_single(conn,'email',{
                    'from_uid':from_uid,
                    'sent_time':int(time.time()),
                    'subject':subject,
                    'body':body,
                    'status':0,
                })).lastrowid
                if len(email_list):
                    await conn.executemany(
                        'INSERT INTO email_rel (email_id,email_id_rel)\
                        VALUES (?,?)',
                        [(email_id,email_id_rel) for email_id_rel in email_list])
                await sql_insert_multi(conn,'recipient',[{
                    'email_id':email_id,
                    'uid':uid,
                    'type':0,
                    'status':0,
                } for uid in to_list]+[{
                    'email_id':email_id,
                    'uid':uid,
                    'type':1,
                    'status':0,
                } for uid in cc_list])
                await conn.commit()
            except Exception as e:
                await conn.rollback()
                raise
        if email_id is not None:
            for uid in to_list:
                if uid not in self._robot:
                    continue
                await self._robot[uid].append(email_id)

    async def mail_recv(self,uid):
        async with self._pool.connection() as conn:
            cursor_total=await conn.execute('SELECT COUNT(id) as total\
                FROM recipient WHERE status>=0 AND uid=?',(uid,))
            cursor_data=await conn.execute('''
                SELECT
                    email.id as id,
                    recipient.type as type,
                    email.subject as subject
                FROM email INNER JOIN recipient ON recipient.email_id=email.id
                WHERE recipient.status>=0 AND recipient.uid=?
                ORDER BY recipient.id DESC''',(uid,))
            return await cursor_data.fetchall(),\
                (await cursor_total.fetchone())['total']

    async def mail_sent(self,uid):
        async with self._pool.connection() as conn:
            cursor_total=await conn.execute('SELECT COUNT(id) as total\
                FROM email WHERE email.status>=0 AND from_uid=?',(uid,))
            cursor_data=await conn.execute('SELECT * FROM email\
                WHERE email.status>=0 AND email.from_uid=? ORDER BY id DESC',
                (uid,))
            return await cursor_data.fetchall(),\
                (await cursor_total.fetchone())['total']

    async def _check_permission(self,conn,uid,email_id):
        cursor=await conn.execute('''SELECT count(id) AS perm FROM email
            where id=? AND (from_uid=? OR id IN (
                SELECT email_id FROM recipient WHERE email_id=? AND uid=?
            ))''',(email_id,uid,email_id,uid))
        return (await cursor.fetchone())['perm']

    async def _get_recipient(self,conn,email_list):
        placeholders = ','.join('?' * len(email_list))
        cursor=await conn.execute(f'SELECT email_id,uid,type FROM recipient\
            WHERE email_id in ({placeholders})',email_list)
        to,cc={},{}
        for item in await cursor.fetchall():
            email_id,uid=item['email_id'],item['uid']
            if email_id not in to:
                to[email_id],cc[email_id]={},{}
            addr=await self.get_addr_from_uid(uid)
            if item['type']==1: #cc
                cc[email_id][uid]=addr
            else:
                to[email_id][uid]=addr
        return to,cc

    async def mail_detail(self,uid,email_id):
        async with self._pool.connection() as conn:
            if not self._check_permission(conn,uid,email_id):
                return None
            cursor=await conn.execute('SELECT * FROM email WHERE id=? OR id IN\
                (SELECT email_id_rel FROM email_rel WHERE email_id=?)\
                ORDER BY id DESC',(email_id,email_id))
            email_list=[{
                'id':email['id'],
                'from_uid':email['from_uid'],
                'from_addr':await self.get_addr_from_uid(email['from_uid']),
                'subject':email['subject'],
                'body':email['body'],
                'sent_time':email['sent_time'],
            } for email in await cursor.fetchall()]
            to,cc=await self._get_recipient(conn,
                [item['id'] for item in email_list])
            for email in email_list:
                email_id=email['id']
                email['to']=to[email_id]
                email['to_str']='; '.join(to[email_id].values())
                email['cc']=cc[email_id]
                email['cc_str']='; '.join(cc[email_id].values())
            return email_list

    async def mark_read(self,uid,email_id):
        async with self._pool.connection() as conn:
            try:
                await conn.execute(
                    'UPDATE recipient SET status=1 WHERE uid=? and email_id=?',
                    (uid,email_id))
                await conn.commit()
            except Exception as e:
                await conn.rollback()
                raise


def MailCenter(app):
    return app['mailCenter']


def setup(app):
    async def __mailcenter_start(app):
        await app['mailCenter'].start()

    async def __mailcenter_stop(app):
        await app['mailCenter'].stop()

    if 'mailCenter' not in app:
        app['mailCenter']=MailCenterInstance(app['config'])
        app.on_startup.append(__mailcenter_start)
        app.on_cleanup.append(__mailcenter_stop)
    return app['mailCenter']

