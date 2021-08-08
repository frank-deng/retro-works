const iconv=require('iconv-lite');
const { FontASC, FontHZK, FontGBK }=require('./font');
const fs=require('fs');

class FontManager{
    __hzkFont={};
    __ascFontList=[];
    __hzkFontList=[];
    constructor(fontData){
        this.__hzkFont={};
        for(let font of fontData){
            if('ASCPS'==font.file){
                this.__ascFont=new FontASC(font.data);
                this.__ascFontList=font.fontNames.slice();
                continue;
            }else if('HZKPST'==font.file){
                this.__hzkSymbolFont=new FontHZK(font.data,true);
                continue;
            }else{
                this.__hzkFont[font.file]=/.GBK$/i.test(font.file) ? new FontGBK(font.data) : new FontHZK(font.data);
                this.__hzkFontList.push({
                    label:font.name,
                    value:font.file
                });
            }
        }
    }
    __checkFontParam(ascFont,hzkFont){
        if(isNaN(ascFont) || null===ascFont || ascFont<0 || ascFont>9){
            throw new ReferenceError('西文字体必须为0-9的数字');
        }
        if(!this.__hzkFont[hzkFont]){
            throw new ReferenceError('指定的中文字体不存在');
        }
    }
    getAscFontList(){
        return this.__ascFontList.map((label,value)=>({
            label,
            value
        }));
    }
    getHzkFontList(){
        return this.__hzkFontList.map(item=>({
            ...item
        }));
    }
    getGlyph(char,ascFont=0,hzkFont){
        //参数检测
        this.__checkFontParam(ascFont,hzkFont);

        let code=char.charCodeAt(0);
        //控制字符不支持
        if(code<0x20){
            return null;
        }
        //作为英文字符处理
        if(code<=0x7e){
            return this.__ascFont ? this.__ascFont.getGlyph(code-0x20,ascFont) : null;
        }
        
        //找到当前中文字体
        let hzkFontInstance=this.__hzkFont[hzkFont];
        if(!hzkFontInstance){
            return null;
        }

        //当前字符无法表示为GB2312或GBK
        let iconvBuf=iconv.encode(char,'GBK');
        if(2!=iconvBuf.length){
            return null;
        }
        let qu=iconvBuf[0], wei=iconvBuf[1];
        
        //GBK字体使用
        if (hzkFontInstance instanceof FontGBK){
            return hzkFontInstance.getGlyph(qu,wei);
        }
        //符号字库使用
        if(qu<0xb0){
            return this.__hzkSymbolFont ? this.__hzkSymbolFont.getGlyph(qu,wei) : null;
        }
        //汉字字库使用
        return hzkFontInstance.getGlyph(qu,wei);
    }
}

async function initFontManager(){
  return new FontManager([
    {
      file:'HZKPSST.GBK',
      name:'HZKPSST.GBK',
      data:await new Promise((resolve,reject)=>{
        fs.readFile('./fontlib/HZKPSST.GBK',null,(err,data)=>{
          if(err){
            reject(err);
            return;
          }
          let len=data.length, arrayBuffer=new ArrayBuffer(len), typedArray=new Uint8Array(arrayBuffer);
          for(let i=0; i<len; i++){
            typedArray[i]=data[i];
          }
          resolve(arrayBuffer);
        });
      })
    }
  ]);
}
module.exports={
  FontManager,
  initFontManager
};

