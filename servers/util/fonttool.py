import re
import glob
from lxml import etree,html

class FontProcessor:
    def __init__(self,font_ascii,font_non_ascii):
        self.__font_ascii=font_ascii
        self.__font_non_ascii=font_non_ascii

    def __apply_font(self,parent,text):
        english_pattern = r'[a-zA-Z0-9\s!-~]+'
        other_pattern = r'( |[^a-zA-Z0-9\s!-~])+'
        pattern = re.compile(f'({english_pattern}|{other_pattern})')
        for match in pattern.finditer(text):
            segment=match.group()
            if re.match(english_pattern, segment):
                e=etree.Element('font')
                e.attrib['face']=self.__font_ascii
                e.text=segment
                parent.append(e)
            else:
                e=etree.Element('font')
                e.attrib['face']=self.__font_non_ascii
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

