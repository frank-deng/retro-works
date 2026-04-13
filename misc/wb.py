#!/usr/bin/env python3

import sys

def mkwbcode(tab_base,word):
    for ch in word:
        if ch not in tab_base:
            return None
    if len(word)==2:
        return tab_base[word[0]][0:2]+tab_base[word[1]][0:2]
    elif len(word)==3:
        return tab_base[word[0]][0]+tab_base[word[1]][0]+\
                tab_base[word[2]][0:2]
    else:
        return tab_base[word[0]][0]+tab_base[word[1]][0]+\
            tab_base[word[2]][0]+tab_base[word[-1]][0]

with open('WB2.TXT','w',newline='\r\n',encoding='gb2312') as dest:
    code_table_base={}
    with open('WB.TXT','r',encoding='gb2312') as fp:
        for line in fp:
            if line.strip():
                dest.write(line)
            hz=line[0]
            code=line[1:].strip()
            if hz not in code_table_base:
                code_table_base[hz]=code
            elif len(code)>len(code_table_base[hz]):
                code_table_base[hz]=code

    for fname in sys.argv[1:]:
        with open(fname,'r',encoding="gb2312") as fp:
            for line in fp:
                word=line.strip()
                if len(word)<2:
                    continue
                code=mkwbcode(code_table_base,word)
                dest.write(f"{word}{code}\n")

