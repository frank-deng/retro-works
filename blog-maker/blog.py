#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import re
import glob
import tomllib
import shutil
from datetime import datetime
import click
import dateutil
import mistune
from jinja2 import Environment,FileSystemLoader

class BlogMaker:
    PARSE_META=0
    PARSE_CONTENT=1
    @staticmethod
    def gen_id(year,month,day,hour,minute):
        CONVTAB='0123456789abcdefghijklmnopqrstuvwxyz'
        return f'{year%100:02d}{CONVTAB[month]}{CONVTAB[day]}{CONVTAB[hour]}{minute:02d}'

    def __init__(self,config_file='blog.toml',output=None):
        self.__config={
            'encoding':"GBK",
            'markdownPath':'posts',
            'defaultLayout':"post.html",
            'outputPath':"dist",
            'font':{
                'ascii':"Times New Roman",
                'cjk':"宋体"
            },
        }
        try:
            with open(config_file, 'rb') as f:
                self.__config.update(tomllib.load(f))
        except FileNotFoundError as e:
            click.echo(click.style(f'Failed to load {config_file}: {e}',fg='red'),err=True)
        except tomllib.TOMLDecodeError as e:
            click.echo(click.style(f'Failed to load {config_file}: {e}',fg='red'),err=True)
        if output is not None:
            self.__config['outputPath']=output
        self.__markdown=mistune.create_markdown(renderer='html',plugins=['table'])
        self.__jinja2=Environment(loader=FileSystemLoader('template')) 

    def __process_markdown(self,fname,fp):
        step=BlogMaker.PARSE_META
        fnparsed=re.findall(r'^(19\d\d|20\d\d)(0\d|1[0-2])([0-2]\d|3[01])_([0-1]\d|2[0-3])([0-5]\d)(.*)?\.md$',fname)
        if fnparsed is None or len(fnparsed)==0:
            click.echo(click.style(f'Misformatted filename {fname}',fg='yellow'))
            return None,None
        year,month,day,hour,minute=[int(n) for n in fnparsed[0][:5]]
        meta={
            'Id':self.__class__.gen_id(year,month,day,hour,minute),
            'Title':fnparsed[0][5].strip(),
            'Tags':[],
            'Date':datetime(year,month,day,hour,minute)
        }
        content=''
        for line in fp:
            if step!=BlogMaker.PARSE_META:
                content+=line
                continue
            line=line.strip()
            if line=='---':
                step=BlogMaker.PARSE_CONTENT
                continue
            key,val=line.split(':')
            key=key.strip()
            val=val.strip()
            if key=='Tags':
                meta[key]=[v.strip() for v in val.split(',')]
            elif key=='Date':
                meta[key]=dateutil.parse(val)
            else:
                meta[key]=val
        content=self.__markdown(content).replace('<strong>','<b>').replace('</strong>','</b>')
        return meta,content

    def __prepare_target(self):
        target_dir=self.__config['outputPath']
        for item in os.listdir(target_dir):
            path_del=os.path.realpath(os.path.join(target_dir,item))
            if os.path.isfile(path_del):
                os.unlink(path_del)
            else:
                shutil.rmtree(path_del)
        shutil.copytree('static',os.path.join(target_dir,'static'))

    def __save_file(self,meta,content):
        template=self.__jinja2.get_template(meta.get('Layout',self.__config['defaultLayout']))
        target_dir=self.__config['outputPath']
        target_file=os.path.join(target_dir,meta['Id']+'.htm')
        encoding=self.__config.get('encoding','UTF-8')
        res=template.render(
            encoding=encoding,
            title=meta.get('Title',''),
            titleProcessed=meta.get('Title',''),
            content=content
        )
        with open(target_file,'wb') as f:
            f.write(res.encode(encoding,'replace'))

    def __save_index(self,postsOrig):
        template=self.__jinja2.get_template('index.html')
        encoding=self.__config.get('encoding','UTF-8')
        posts=[]
        for item in postsOrig:
            posts.append({
                'link':item['Id']+'.htm',
                'tags':item['Tags'],
                'title':item['Title']
            })
        res=template.render(encoding=encoding,posts=posts)
        with open(os.path.join(self.__config['outputPath'],'index.htm'),'wb') as f:
            f.write(res.encode(encoding,'replace'))

    def parse(self):
        self.__prepare_target()
        files=[f for f in glob.glob(os.path.join(self.__config['markdownPath'],'*.md')) if os.path.isfile(f)]
        files.sort()
        idx=0
        posts=[]
        for file in files:
            with open(file,'r',encoding='utf-8') as fp:
                meta,content=self.__process_markdown(os.path.basename(file),fp)
                if meta is None or content is None:
                    continue
                self.__save_file(meta,content)
                posts.append(meta)
                idx=idx+1
        self.__save_index(posts)


@click.group(invoke_without_command=True)
@click.option('--config_file','-c',default='blog.toml',
              help='Specify TOML config file.')
@click.option('--output','-o',default=None,
              help='Specify Output Path')
@click.pass_context
def main(ctx,config_file,output):
    sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
    blogMaker=BlogMaker(config_file,output)
    blogMaker.parse()

if '__main__'==__name__:
    main()

