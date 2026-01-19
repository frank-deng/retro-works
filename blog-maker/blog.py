#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import re
import glob
import tomllib
import shutil
import json
from datetime import datetime
import click
import csv
from io import StringIO
import dateutil
import markdown2
from jinja2 import Environment,FileSystemLoader
from lxml import etree,html

class FontProcessor:
    def __init__(self,conf):
        self.__config=conf

    def __apply_font(self,parent,text):
        english_pattern = r'[a-zA-Z0-9\s!-~]+'
        other_pattern = r'( |[^a-zA-Z0-9\s!-~])+'
        pattern = re.compile(f'({english_pattern}|{other_pattern})')
        for match in pattern.finditer(text):
            segment=match.group()
            if re.match(english_pattern, segment):
                e=etree.Element('font')
                e.attrib['face']=self.__config['font']['ascii']
                e.text=segment
                parent.append(e)
            else:
                e=etree.Element('font')
                e.attrib['face']=self.__config['font']['cjk']
                e.text=segment
                parent.append(e)

    def __copy_element(self,parent_old,parent_new):
        for item in parent_old:
            if isinstance(item,etree._Comment):
                continue
            tag=item.tag
            item_new=etree.Element(tag)
            parent_new.append(item_new)
            for key,value in item.attrib.items():
                item_new.set(key,value)
            item_new.text=item.text
            item_new.tail=item.tail
            self.__copy_element(item,item_new)

    def __process_element(self,parent_old,parent_new):
        for item in parent_old:
            if isinstance(item,etree._Comment):
                continue
            tag=item.tag
            if tag=='strong':
                tag='b'
            item_new=etree.Element(tag)
            parent_new.append(item_new)
            for key,value in item.attrib.items():
                item_new.set(key,value)
            if tag in ('pre','code'):
                item_new.text=item.text
                self.__copy_element(item,item_new)
            else:
                if item.text and item.text.strip():
                    self.__apply_font(item_new,item.text)
                self.__process_element(item,item_new)
            if item.tail and item.tail.strip():
                self.__apply_font(parent_new,item.tail)

    def apply_font(self,content,singleLine=False):
        old_tree=html.fromstring("<html>"+content+"</html>")
        new_tree=html.document_fromstring("<html></html>")
        self.__process_element(old_tree,new_tree)
        res=html.tostring(new_tree,encoding='utf-8').decode('utf-8')
        res=re.sub(r'^\<html\>\<body\>','',res)
        res=re.sub(r'\</body\>\</html\>$','',res)
        if singleLine:
            res=re.sub(r'^\<p\>','',res)
            res=re.sub(r'\</p\>$','',res)
        return res


class DefaultProcessor(FontProcessor):
    def __init__(self,conf):
        super().__init__(conf)

    def parse(self,meta,content):
        html=markdown2.markdown(content,extras=['tables'])
        return self.apply_font(meta.get('Title','')),self.apply_font(html)


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
        self.__jinja2=Environment(loader=FileSystemLoader('template'))
        self.__defaultProcessor=DefaultProcessor(self.__config)

    def __process_file(self,fname,fp):
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
                meta[key]=[v.strip() for v in next(csv.reader(StringIO(val)))]
            elif key=='Date':
                meta[key]=dateutil.parse(val)
            else:
                meta[key]=val
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

    def __save_file(self,meta,titleProcessed,content):
        template=self.__jinja2.get_template(meta.get('Layout',self.__config['defaultLayout']))
        target_dir=self.__config['outputPath']
        target_file=os.path.join(target_dir,meta['Id']+'.htm')
        encoding=self.__config.get('encoding','UTF-8')
        res=template.render(
            encoding=encoding,
            title=meta.get('Title',''),
            titleProcessed=titleProcessed,
            date=meta['Date'].strftime('%Y-%m-%d %H:%M'),
            content=content
        )
        with open(target_file,'wb') as f:
            f.write(res.encode(encoding,'replace'))

    def __save_index(self,postsOrig):
        fontProc=FontProcessor(self.__config)
        template=self.__jinja2.get_template('index.html')
        encoding=self.__config.get('encoding','UTF-8')
        postsJson=[]
        postsRender=[]
        for item in postsOrig:
            postsJson.append({
                'link':item['Id']+'.htm',
                'tags':item['Tags'],
                'title':item['Title']
            })
            postsRender.append({
                'link':item['Id']+'.htm',
                'tags':fontProc.apply_font('、'.join(item['Tags']),True),
                'title':item['Title']
            })
        res=template.render(encoding=encoding,posts=postsRender)
        with open(os.path.join(self.__config['outputPath'],'index.htm'),'wb') as f:
            f.write(res.encode(encoding,'replace'))
        jsonFile=self.__config.get('jsonFile')
        if jsonFile:
            with open(os.path.join(self.__config['outputPath'],jsonFile),'w') as f:
                f.write(json.dumps(postsJson,indent=2,ensure_ascii=False))

    def parse(self):
        self.__prepare_target()
        files=[f for f in glob.glob(os.path.join(self.__config['markdownPath'],'*.md')) if os.path.isfile(f)]
        files.sort()
        files.reverse()
        idx=0
        posts=[]
        for file in files:
            with open(file,'r',encoding='utf-8') as fp:
                meta,content=self.__process_file(os.path.basename(file),fp)
                if meta is None or content is None:
                    continue
                title,content=self.__defaultProcessor.parse(meta,content)
                self.__save_file(meta,title,content)
                posts.append(meta)
                idx=idx+1
        if len(posts)==0:
            click.echo(click.style(f'No article processed',fg='yellow'))
        else:
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

