#!/usr/bin/env python3

MB_HEADER="""[Description]
Name=五笔字形
MaxCodes=4
UsedCodes=abcdefghijklmnopqrstuvwxy
WildChar=z
Sort=1
[TEXT]
"""

import argparse,re

def loadmb(fpath):
    mb_single=[]
    mb_base={}
    with open(fpath,'r',encoding='gb2312') as fp:
        for line in fp:
            line=line.strip()
            if not line or line[0]<'a' or line[0]>'y':
                continue
            items=line.split()
            code=items[0]
            for hz in items[1:]:
                hz=re.sub(r'[\x00-\x7f]','',hz)
                if len(hz)>1:
                    continue
                mb_single.append((hz,code))
                if len(mb_base.get(hz,''))<len(code):
                    mb_base[hz]=code
    mb_single=sorted(mb_single,key=lambda a:a[1])
    return mb_single,mb_base

def wbcode(mb,w):
    code=[mb[ch] for ch in w]
    if len(w)==2:
        return code[0][0:2]+code[1][0:2]
    elif len(w)==3:
        return code[0][0]+code[1][0]+code[2][0:2]
    else:
        return code[0][0]+code[1][0]+code[2][0]+code[-1][0]

if '__main__'==__name__:
    parser = argparse.ArgumentParser(description="Wubi code table generator")
    parser.add_argument('-b', dest='base_file', default='WB.DIC', help='Base code table file')
    parser.add_argument('-o', dest='output_file', default='WB.TXT', help='Output file')
    parser.add_argument('-s', action='store_true', help='Sort generated code table')
    parser.add_argument('input_files', nargs='*', help='Input files')
    args = parser.parse_args()
    mb_final,mb_base=loadmb(args.base_file)
    mb_words={}
    for fname in args.input_files:
        with open(fname,'r',encoding="gb2312") as fp:
            for line in fp:
                word=line.strip()
                if len(word)<2 or word in mb_words:
                    continue
                mb_words[word]=wbcode(mb_base,word)
    mb_final+=sorted(mb_words.items(),key=lambda a:a[1])
    if args.s:
        mb_final=sorted(mb_final,key=lambda a:a[1])
    with open(args.output_file,'w',newline='\r\n',encoding='gb2312') as fp:
        fp.write(MB_HEADER)
        for item in mb_final:
            fp.write(f'{item[0]}{item[1]}\n')

