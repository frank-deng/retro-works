#!/usr/bin/env python3

import logging
import sys
import tomllib
import importlib
import asyncio
import signal
import click
import os
import platform
import time
from util import Logger
from util.watchdog import watchdog
from util.daemon import daemonize
from util.daemon import stop_daemon
from util.daemon import DaemonIsRunningError
from util.daemon import DaemonNotRunningError
from util.daemon import DaemonAbnormalExitError


class ServiceManager(Logger):
    def __init__(self,config):
        self.__conf=config
        self.__modules=[]
        for module in config['modules']:
            server_instance=self.__server_init(module,self.__conf)
            if server_instance is None:
                continue
            self.__modules.append(server_instance)
        if not len(self.__modules):
            raise RuntimeError('None of the modules has been started')

    def __server_init(self,module_path,config):
        server_instance=None
        try:
            selector=None
            if ':' in module_path:
                module_path,selector=module_path.split(':')
            module=importlib.import_module(module_path)
            if selector is not None:
                module=getattr(module,selector)
            server_instance=module(config)
        except Exception as e:
            self.logger.error(f'Failed to load server {server_key}: {e}',
                              exc_info=True)
        return server_instance

    async def __aenter__(self):
        tasks=await asyncio.gather(*[self.__module_aenter(s) \
                for s in self.__modules])
        for i in range(len(tasks)-1,-1,-1):
            _,e=tasks[i]
            if e is not None:
                del self.__modules[i]
        return self

    async def __module_aenter(self,server):
        try:
            res=await server.__aenter__()
            return res,None
        except Exception as e:
            self.logger.error(e,exc_info=True)
            return None,e

    async def __aexit__(self,exc_type,exc_val,exc_tb):
        await asyncio.gather(*[self.__module_aexit(s,exc_type,exc_val,exc_tb) \
                for s in self.__modules])

    async def __module_aexit(self,server,exc_type,exc_val,exc_tb):
        try:
            await server.__aexit__(exc_type,exc_val,exc_tb)
        except Exception as e:
            self.logger.error(e,exc_info=True)

    def close(self):
        for server in self.__modules:
            server.close()


@watchdog('watchdog_timeout')
async def async_main(config):
    try:
        async with ServiceManager(config) as service_manager:
            register_close_signal(service_manager.close)
    except Exception as e:
        logging.getLogger(__name__).critical(e,exc_info=True)


def register_close_signal(func):
    loop = asyncio.get_event_loop()
    if 'Windows'==platform.system():
        for s in (signal.SIGINT, signal.SIGTERM):
            signal.signal(s,func)
    else:
        for s in (signal.SIGINT,signal.SIGTERM,signal.SIGQUIT):
            loop.add_signal_handler(s,func)


@daemonize('pid_file','detach')
def server_main(config):
    logging.basicConfig(
        format='[%(asctime)s][%(levelname)s]%(message)s',
        filename=config.get('log_file','server.log'),
        level=getattr(logging,config.get('log_level','INFO'),logging.INFO)
    )
    try:
        asyncio.run(async_main(config))
        logging.getLogger(__name__).info('Server closed')
    except Exception as e:
        logging.getLogger(__name__).critical(e,exc_info=True)


@click.group(invoke_without_command=True)
@click.option('--config_file','-c',default='server.toml',
              help='Specify TOML config file.')
@click.pass_context
def cli(ctx,config_file):
    sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
    config=None
    try:
        with open(config_file, 'rb') as f:
            config=tomllib.load(f)
    except FileNotFoundError as e:
        click.echo(click.style(f'Failed to load {config_file}: {e}',fg='red'),err=True)
        ctx.exit(code=1)
    except tomllib.TOMLDecodeError as e:
        click.echo(click.style(f'Failed to load {config_file}: {e}',fg='red'),err=True)
        ctx.exit(code=1)
    ctx.obj=config
    if ctx.invoked_subcommand is None:
        try:
            server_main(config)
        except DaemonIsRunningError as e:
            click.echo(click.style(f'Server is already running',fg='red'),err=True)
            ctx.exit(code=1)

@cli.command()
@click.pass_context
def stop(ctx):
    if 'win32'==sys.platform:
        click.echo(click.style(f'Stopping server on Windows is not supported yet.',fg='red'),err=True)
        ctx.exit(1)

    config=ctx.obj
    if 'pid_file' not in config:
        click.echo(click.style(f'PID file not specified in the config file.',fg='yellow'),err=True)
        ctx.exit(1)
    try:
        stop_daemon(config['pid_file'])
    except DaemonNotRunningError:
        click.echo(click.style(f'Server is not running.',fg='yellow'),err=True)
        ctx.exit(code=1)
    except DaemonAbnormalExitError:
        click.echo(click.style(f'Server may have shutdown abnormally, please check server\'s log for detail.',fg='yellow'),err=True)
        ctx.exit(code=1)


if '__main__'==__name__:
    cli()
