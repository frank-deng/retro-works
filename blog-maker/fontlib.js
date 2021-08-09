Object.defineProperty(exports, '__esModule', { value: true });

var iconv = require('iconv-lite');

function _interopDefaultLegacy (e) { return e && typeof e === 'object' && 'default' in e ? e : { 'default': e }; }

var iconv__default = /*#__PURE__*/_interopDefaultLegacy(iconv);

function calculateBezierPoint(fraction,...args){
    let xCalc=[], yCalc=[], xTemp=[], yTemp=[], counter=1000;
    for(let i=0; i<args.length; i+=2){
        xCalc.push(args[i]);
        yCalc.push(args[i+1]);
    }
    while(xCalc.length>1 && --counter){
        let len=xCalc.length-1;
        for(let i=0; i<len; i++){
            xTemp.push(xCalc[i]+(xCalc[i+1]-xCalc[i])*fraction);
            yTemp.push(yCalc[i]+(yCalc[i+1]-yCalc[i])*fraction);
        }
        xCalc=xTemp;
        yCalc=yTemp;
        xTemp=[];
        yTemp=[];
    }
    if(counter<=0){
        throw new Error('Dead loop');
    }
    return {
        x:xCalc[0],
        y:yCalc[0]
    };
}
class PathElement{
    constructor(){
        if (PathElement==this.constructor) {
            throw new Error("Abstract classes can't be instantiated.");
        }
    }
    __init__(item){
        if(!(item instanceof this.constructor)){
            throw new TypeError('Source object must be instance of PathElement');
        }
        if(undefined!==this.xStart && undefined!==this.yStart){
            item.setPos(this.xStart,this.yStart);
        }
        return item;
    }
    clone(){
        throw new Error('clone() method not implemented');
    }
    setPos(xStart,yStart){
        Object.assign(this,{
            xStart,
            yStart
        });
        return this;
    }
    getPos(){
        if(undefined===this.xStart || undefined===this.yStart){
            throw new Error('Start position not specified');
        }
        return {
            x:this.xStart,
            y:this.yStart
        };
    }
}
class MoveTo extends PathElement{
    constructor(x,y){
        super();
        Object.assign(this,{
            x,y
        });
    }
    clone(){
        return new this.constructor(this.x,this.y);
    }
    next(){
        return {
            x:this.x,
            y:this.y
        };
    }
    getBoundingRect(){
        throw new Error(`Bounding rectangle calculation not available for MoveTo`);
    }
    toSVG(){
        return `M${this.x} ${this.y}`;
    }
}
class Rect extends PathElement{
    constructor(x0,y0,x1,y1){
        super();
        Object.assign(this,{
            x0,y0,x1,y1
        });
    }
    clone(){
        return new this.constructor(this.x0,this.y0,this.x1,this.y1);
    }
    toSVG(){
        let {x0,y0,x1,y1}=this;
        return `M${x0} ${y0} H${x1} V${y1} H${x0} V${y0} Z`
    }
    getBoundingRect(){
        return {
            x0:Math.min(this.x0,this.x1),
            y0:Math.min(this.y0,this.y1),
            x1:Math.max(this.x0,this.x1),
            y1:Math.max(this.y0,this.y1),
        }
    }
}
class HorLineTo extends PathElement{
    constructor(x){
        super();
        Object.assign(this,{
            x
        });
    }
    clone(){
        return super.__init__(new this.constructor(this.x));
    }
    next(){
        return {
            x:this.x,
            y:this.yStart
        };
    }
    getBoundingRect(){
        let {x,y}=this.getPos();
        return {
            x0:Math.min(x,this.x),
            y0:y,
            x1:Math.max(x,this.x),
            y1:y
        }
    }
    toSVG(){
        return `H${this.x}`;
    }
}
class VerLineTo extends PathElement{
    constructor(y){
        super();
        Object.assign(this,{
            y
        });
    }
    clone(){
        return super.__init__(new this.constructor(this.y));
    }
    next(){
        return {
            x:this.xStart,
            y:this.y
        };
    }
    getBoundingRect(){
        let {x,y}=this.getPos();
        return {
            x0:x,
            y0:Math.min(y,this.y),
            x1:x,
            y1:Math.max(y,this.y)
        }
    }
    toSVG(){
        return `V${this.y}`;
    }
}
class LineTo extends PathElement{
    constructor(x,y,rx=false,ry=false){
        super();
        Object.assign(this,{
            x,y,rx,ry
        });
    }
    clone(){
        return super.__init__(new this.constructor(this.x,this.y,this.rx,this.ry));
    }
    next(){
        return {
            x:this.rx ? this.xStart+this.x : this.x,
            y:this.ry ? this.yStart+this.y : this.y
        };
    }
    getBoundingRect(){
        let {x,y}=this.getPos();
        let pos=this.next();
        return {
            x0:Math.min(x,pos.x),
            y0:Math.min(y,pos.y),
            x1:Math.max(x,pos.x),
            y1:Math.max(y,pos.y)
        }
    }
    toSVG(){
        if(!this.rx && !this.ry){
            return `L${this.x} ${this.y}`;
        }else if(this.rx && this.ry){
            return `l${this.x} ${this.y}`;
        }
        let {x,y}=this.getPos();
        return `L${this.rx ? x+this.x : this.x} ${this.ry ? y+this.y : this.y}`;
    }
}
class QuadCurveTo extends PathElement{
    __boundingRect=null;
    constructor(x0,y0,x1,y1,relative=false){
        super();
        Object.assign(this,{
            x0,y0,x1,y1,relative
        });
    }
    __calculateBoundingRect(){
        let x=this.xStart,
            y=this.yStart,
            x0=this.relative ? x+this.x0 : this.x0,
            y0=this.relative ? y+this.y0 : this.y0,
            x1=this.relative ? x+this.x1 : this.x1,
            y1=this.relative ? y+this.y1 : this.y1,
            xMin=x, xMax=x, yMin=y, yMax=y;
        const FRACTION=100;
        for(let i=0; i<FRACTION; i++){
            let p=calculateBezierPoint(i/FRACTION,x,y,x0,y0,x1,y1);
            xMin=Math.min(xMin,p.x);
            yMin=Math.min(yMin,p.y);
            xMax=Math.max(xMax,p.x);
            yMax=Math.max(yMax,p.y);
        }
        this.__boundingRect={
            x0:Math.floor(xMin),
            y0:Math.floor(yMin),
            x1:Math.ceil(xMax),
            y1:Math.ceil(yMax)
        };
    }
    setPos(x,y){
        super.setPos(x,y);
        this.__calculateBoundingRect();
        return this;
    }
    clone(){
        return (new this.constructor(this.x0,this.y0,this.x1,this.y1,this.relative)).setPos(this.xStart,this.yStart);
    }
    next(){
        return {
            x:this.relative ? this.xStart+this.x1 : this.x1,
            y:this.relative ? this.yStart+this.y1 : this.y1
        };
    }
    getBoundingRect(){
        if(!this.__boundingRect){
            throw new Error('Start position not set');
        }
        return {
            ...this.__boundingRect
        };
    }
    toSVG(){
        return `${this.relative ? 'q' : 'Q'}${this.x0} ${this.y0}, ${this.x1} ${this.y1}`;
    }
}
class CurveTo extends PathElement{
    __boundingRect=null;
    constructor(x0,y0,x1,y1,x2,y2,relative=false){
        super();
        Object.assign(this,{
            x0,y0,x1,y1,x2,y2,relative
        });
    }
    clone(){
        return (new this.constructor(this.x0,this.y0,this.x1,this.y1,this.x2,this.y2,this.relative)).setPos(this.xStart,this.yStart);
    }
    __calculateBoundingRect(){
        let x=this.xStart,
            y=this.yStart,
            x0=this.relative ? x+this.x0 : this.x0,
            y0=this.relative ? y+this.y0 : this.y0,
            x1=this.relative ? x+this.x1 : this.x1,
            y1=this.relative ? y+this.y1 : this.y1,
            x2=this.relative ? x+this.x2 : this.x2,
            y2=this.relative ? y+this.y2 : this.y2,
            xMin=x, xMax=x, yMin=y, yMax=y;
        const FRACTION=100;
        for(let i=0; i<FRACTION; i++){
            let p=calculateBezierPoint(i/FRACTION,x,y,x0,y0,x1,y1,x2,y2);
            xMin=Math.min(xMin,p.x);
            yMin=Math.min(yMin,p.y);
            xMax=Math.max(xMax,p.x);
            yMax=Math.max(yMax,p.y);
        }
        this.__boundingRect={
            x0:Math.floor(xMin),
            y0:Math.floor(yMin),
            x1:Math.ceil(xMax),
            y1:Math.ceil(yMax)
        };
    }
    setPos(x,y){
        super.setPos(x,y);
        this.__calculateBoundingRect();
        return this;
    }
    next(){
        return {
            x:this.relative ? this.xStart+this.x2 : this.x2,
            y:this.relative ? this.yStart+this.y2 : this.y2
        };
    }
    getBoundingRect(){
        if(!this.__boundingRect){
            throw new Error('Start position not set');
        }
        return {
            ...this.__boundingRect
        };
    }
    toSVG(){
        return `${this.relative ? 'c' : 'C'}${this.x0} ${this.y0}, ${this.x1} ${this.y1}, ${this.x2} ${this.y2}`;
    }
}

class Path{
    __strokeList=[];
    __closedPath=true;
    __x=0;
    __y=0;
    __bbox={
        x0:null,
        y0:null,
        x1:null,
        y1:null
    }
    constructor(src=[]){
        let strokeList=src;
        if(src instanceof Path){
            strokeList=src.__strokeList;
        }else if(!Array.isArray(src)){
            throw new TypeError('Initialization parameter must be either an array or an instance of Path class');
        }
        for(let item of strokeList){
            this.add(item);
        }
    }
    reset(){
        Object.assign(this,{
            __strokeList:[],
            __bbox:{
                x0:null,
                y0:null,
                x1:null,
                y1:null
            },
            __x:0,
            __y:0
        });
    }
    __calculateBoundingRect(item){
        try{
            let bbox=item.getBoundingRect();
            let {x0,y0,x1,y1}=this.__bbox;
            let xMin=Math.floor(Math.min(bbox.x0,bbox.x1)),
                xMax=Math.ceil(Math.max(bbox.x0,bbox.x1)),
                yMin=Math.floor(Math.min(bbox.y0,bbox.y1)),
                yMax=Math.ceil(Math.max(bbox.y0,bbox.y1));
            if(null===x0 || xMin<x0){
                x0=xMin;
            }
            if(null===x1 || xMax>x1){
                x1=xMax;
            }
            if(null===y0 || yMin<y0){
                y0=yMin;
            }
            if(null===y1 || yMax>y1){
                y1=yMax;
            }
            Object.assign(this.__bbox,{
                x0,y0,x1,y1
            });
        }catch(e){
            console.error('Failed to update bounding box',e);
        }
    }
    add(itemOrig){
        if(!(itemOrig instanceof PathElement)){
            throw new TypeError('Item must inherit class PathElement');
        }
        let item=itemOrig.clone();

        //对画方形操作做特殊处理
        if(item instanceof Rect){
            this.__strokeList.unshift(item);
            this.__calculateBoundingRect(item);
            return;
        }
        
        this.__strokeList.push(item);
        if(!(item instanceof MoveTo)){
            item.setPos(this.__x,this.__y);
            this.__calculateBoundingRect(item);
        }
        let nextPos=item.next();
        Object.assign(this,{
            __x:nextPos.x,
            __y:nextPos.y
        });
    }
    getBoundingRect(){
        if(this.isEmpty()){
            return null;
        }
        return {
            ...this.__bbox
        };
    }
    isEmpty(){
        for(let item of this.__strokeList){
            if(item instanceof MoveTo){
                continue;
            }
            return false;
        }
        return true;
    }
    setClosedPath(val=true){
        this.__closedPath=!!val;
    }
    toSVG(){
        if(this.isEmpty()){
            return null;
        }
        return this.__strokeList.map(item=>item.toSVG()).join(' ')+(this.__closedPath ? ' Z' : '');
    }
}

function getNum8(data,offset){
    return (data[offset]<<4)|data[offset+1];
}
function getNum4(data,offset){
    let value=data[offset], num=value&7;
    return value&8 ? -num : num;
}
function getNum6Pair(data,offset){
    let n0=(data[offset]<<2)|(data[offset+1]>>2),
        n1=((data[offset+1]&3)<<4)|data[offset+2];
    let s0=n0&32, s1=n1&32;
    n0&=31; n1&=31;
    return [s0 ? -n0 : n0, s1 ? -n1 : n1];
}
class Font{
    __cache={};
    constructor(fontData){
        if (Font==this.constructor) {
            throw new Error("Abstract classes can't be instantiated.");
        }
        this.__arrayBuffer=fontData;
        this.__dataView=new DataView(this.__arrayBuffer);
    }
    __getGlyphData(idx){
        let dataView=this.__dataView, offset=idx*6;
        let dataOffset=dataView.getUint32(offset,true)&0xfffffff;
        let dataLen=dataView.getUint16(offset+4,true);
        if(!dataLen){
            return null;
        }
        let array=new Uint8Array(this.__arrayBuffer,dataOffset,dataLen);
        let result=[];
        for(let value of array){
            result.push(value&0xf);
            result.push((value>>4)&0xf);
        }
        return result;
    }
    __processGlyphData(data){
        let ctrlTable={
            0:{
                step:4,
                processor(data,offset){
                    return new MoveTo(getNum8(data,offset), getNum8(data,offset+2));
                }
            },
            1:{
                step:2,
                processor(data,offset){
                    return new HorLineTo(getNum8(data,offset));
                }
            },
            2:{
                step:2,
                processor(data,offset){
                    return new VerLineTo(getNum8(data,offset));
                }
            },
            3:{
                step:4,
                processor(data,offset){
                    return new LineTo(getNum8(data,offset), getNum8(data,offset+2));
                }
            },
            4:{
                step:8,
                processor(data,offset){
                    return new QuadCurveTo(
                        getNum8(data,offset),
                        getNum8(data,offset+2),
                        getNum8(data,offset+4),
                        getNum8(data,offset+6)
                    );
                }
            },
            5:{
                step:12,
                processor(data,offset){
                    return new CurveTo(
                        getNum8(data,offset),
                        getNum8(data,offset+2),
                        getNum8(data,offset+4),
                        getNum8(data,offset+6),
                        getNum8(data,offset+8),
                        getNum8(data,offset+10)
                    );
                }
            },
            6:{
                step:8,
                processor(data,offset){
                    return new Rect(
                        getNum8(data,offset),
                        getNum8(data,offset+2),
                        getNum8(data,offset+4),
                        getNum8(data,offset+6)
                    );
                }
            },
            7:{
                step:3,
                processor(data,offset){
                    return new LineTo(getNum4(data,offset),getNum8(data,offset+1),true,false);
                }
            },
            8:{
                step:3,
                processor(data,offset){
                    return new LineTo(getNum8(data,offset),getNum4(data,offset+2),false,true);
                }
            },
            9:{
                step:2,
                processor(data,offset){
                    return new LineTo(getNum4(data,offset),getNum4(data,offset+1),true,true);
                }
            },
            10:{
                step:3,
                processor(data,offset){
                    let [dx,dy]=getNum6Pair(data,offset);
                    return new LineTo(dx,dy,true,true);
                }
            },
            11:{
                step:4,
                processor(data,offset){
                    let dx0=getNum4(data,offset),
                        dy0=getNum4(data,offset+1),
                        dx1=getNum4(data,offset+2),
                        dy1=getNum4(data,offset+3);
                    return new QuadCurveTo(dx0,dy0,dx0+dx1,dy0+dy1,true);
                }
            },
            12:{
                step:6,
                processor(data,offset){
                    let [dx0,dy0]=getNum6Pair(data,offset);
                    let [dx1,dy1]=getNum6Pair(data,offset+3);
                    return new QuadCurveTo(dx0,dy0,dx0+dx1,dy0+dy1,true);
                }
            },
            13:{
                step:6,
                processor(data,offset){
                    let dx0=getNum4(data,offset),
                        dy0=getNum4(data,offset+1),
                        dx1=getNum4(data,offset+2),
                        dy1=getNum4(data,offset+3),
                        dx2=getNum4(data,offset+4),
                        dy2=getNum4(data,offset+5);
                    return new CurveTo(
                        dx0,
                        dy0,
                        dx0+dx1,
                        dy0+dy1,
                        dx0+dx1+dx2,
                        dy0+dy1+dy2,
                        true);
                }
            },
            14:{
                step:9,
                processor(data,offset){
                    let [dx0,dy0]=getNum6Pair(data,offset);
                    let [dx1,dy1]=getNum6Pair(data,offset+3);
                    let [dx2,dy2]=getNum6Pair(data,offset+6);
                    return new CurveTo(
                        dx0,
                        dy0,
                        dx0+dx1,
                        dy0+dy1,
                        dx0+dx1+dx2,
                        dy0+dy1+dy2,
                        true);
                }
            },
            15:{
                step:4,
                processor(data,offset){}
            }
        };
        let idx=0,path=new Path(),counter=10000;
        while(idx<=data.length && counter--){
            let ctrl=ctrlTable[data[idx]];
            idx++;
            if(idx>=data.length){
                break;
            }
            let pathElement=ctrl.processor(data,idx);
            idx+=ctrl.step;
            if(pathElement){
                path.add(pathElement);
            }
        }
        if(!counter){
            throw new Error('Dead loop detected');
        }
        return path;
    }
    getGlyph(idx){
        if(this.__cache[idx]){
            return this.__cache[idx];
        }
        let glyphData=this.__getGlyphData(idx);
        if(!glyphData || !glyphData.length){
            return new Path();
        }
        let path=this.__processGlyphData(glyphData);
        this.__cache[idx]=path;
        return path;
    }
}
class Glyph extends Path{
    static BASE_HEIGHT=170;
    static ASCII_BASE_HEIGHT=128;
    __marginLeft=0;
    __marginRight=0;
    constructor(src,ascii=true){
        super(src);
        this.__ascii=ascii;
    }
    add(param){
        super.add(param);
    }
    isAscii(){
        return this.__ascii;
    }
    getWidth(){
        if(!this.isAscii()){
            return Glyph.BASE_HEIGHT;
        }else if(this.isEmpty()){
            return Math.round(Glyph.ASCII_BASE_HEIGHT/2);
        }else {
            return this.getBoundingRect().x1*1.21;
        }
    }
}
class FontASC extends Font{
    constructor(fontData){
        super(fontData);
    }
    getGlyph(charIdx,fontIdx=0){
        if(charIdx<0x20){
            return null;
        }
        if(0x20==charIdx){
            return new Glyph();
        }
        return new Glyph(super.getGlyph((charIdx-0x21)+fontIdx*94));
    }
}
class FontHZK extends Font{
    constructor(fontData,isSymbol=false){
        super(fontData);
        this.__isSymbol=isSymbol;
    }
    getGlyph(qu,wei){
        if(wei<0xa1 || wei>0xfe){
            return null;
        }
        if((this.__isSymbol && (qu<0xa1 || qu>0xa9))
            || (!this.__isSymbol && (qu<0xb0 || qu>0xf7))){
            return null;
        }
        return new Glyph(super.getGlyph((this.__isSymbol ? qu-0xa1 : qu-0xb0)*94+(wei-0xa1)),false);
    }
}
class FontGBK extends Font{
    constructor(fontData){
        super(fontData);
    }
    getGlyph(qu,wei){
        let offset=-1;
        if(qu<0x81 || qu>0xfe || wei<0x40 || wei==0x7f || wei>0xfe){
            return null;
        }
        if(wei<0x7f){
            offset=0x2e44+(qu-0x81)*96+(wei-0x40);
        }else if(wei<0xa1){
            offset=0x2e44+(qu-0x81)*96+(wei-0x41);
        }else if(qu<0xa1){
            offset=0x2284+(qu-0x81)*94+(wei-0xa1);
        }else {
            offset=(qu-0xa1)*94+(wei-0xa1);
        }
        if(offset<0){
            return null;
        }
        try{
            return new Glyph(super.getGlyph(offset),false);
        }catch(e){
            console.error(e);
        }
        return null;
    }
}

function processNumber(num){
    if(num&0x40){
        num=~((~num)&0x3f);
    }else {
        num&=0x3f;
    }
    return num;
}
class GlyphBGI extends Path{
    __width=0;
    __height=0;
    constructor(param,font){
        super(param);
        super.setClosedPath(false);
    }
    setWidth(value){
        this.__width=value;
        return this;
    }
    getWidth(){
        return this.__width;
    }
    setHeight(value){
        this.__height=value;
        return this;
    }
    getHeight(){
        return this.__height;
    }
}
class FontBGI{
    __cache={};
    constructor(fontData){
        this.__arrayBuffer=fontData;
        this.__dataView=new DataView(this.__arrayBuffer);

        //Get prefix text and font header offset
        let prefix=new Uint8Array(this.__arrayBuffer,0,0x80);
        let prefixText='', fontHeaderOffset=0;
        for(let v of prefix){
            fontHeaderOffset++;
            if(0x1a==v){
                break;
            }
            prefixText+=String.fromCharCode(v);
        }
        console.info(prefixText);

        let fontHeader=new DataView(this.__arrayBuffer.slice(fontHeaderOffset,fontHeaderOffset+12));
        let headerSize=fontHeader.getUint16(0,true);
        if(0x80!=headerSize){
            console.warn(`Incorrect header size: expected 0x80, got 0x${headerSize.toString(16)}`);
        }

        this.__fontName=new TextDecoder().decode(new Uint8Array(fontHeader.buffer.slice(2,6)));

        let fontSize=fontHeader.getUint16(6,true);
        if(fontSize!=this.__arrayBuffer.byteLength-0x80){
            console.warn(`Font size check failed: expected ${fontSize}, got ${this.__arrayBuffer.byteLength-0x80}`);
        }

        //Display version info
        console.info('Driver Version:', fontHeader.getInt16(8,true), '; BGI Revision', fontHeader.getInt16(10,true));

        //Get header info
        let header=new DataView(this.__arrayBuffer.slice(headerSize,headerSize+16));
        let signature=header.getUint8(0);
        if(0x2b!=signature){
            throw new ReferenceError(`Error reading font file: expected 0x2b, got 0x${signature.toString(16)}`);
        }
        let charCount=this.__charCount=header.getUint16(1,true);
        this.__firstChar=header.getUint8(4);
        let strokeOffset=header.getUint16(5,true);
        let scanable=header.getUint8(7);

        this.__top=header.getInt8(8);
        this.__baseLine=header.getInt8(9);
        this.__bottom=header.getInt8(10);
        //console.log('top,base,bottom',this.__top,this.__baseLine,this.__bottom);

        let offsetTableOffset=headerSize+16,
            widthTableOffset=offsetTableOffset+charCount*2;
        this.__baseOffset=widthTableOffset+charCount;
        this.__offset=new Uint16Array(this.__arrayBuffer.slice(offsetTableOffset,widthTableOffset));
        this.__width=new Uint8Array(this.__arrayBuffer.slice(widthTableOffset,this.__baseOffset));
    }
    getFontName(){
        return this.__fontName;
    }
    getGlyph(idx,fontSize=16,fontRatio=1){
        if(idx<this.__firstChar || idx>=(this.__firstChar+this.__charCount)){
            return null;
        }
        idx-=this.__firstChar;
        let offset=this.__baseOffset+this.__offset[idx], counter=100000, path=new GlyphBGI();
        let baseHeight=Math.abs(this.__bottom-this.__top);
        let x=0, y=0, scale=fontSize/baseHeight;
        path.setWidth(this.__width[idx]*scale*fontRatio).setHeight(baseHeight*scale);
        while(counter--){
            let dx=this.__dataView.getUint8(offset);offset++;
            let dy=this.__dataView.getUint8(offset);offset++;
            let oper=0;
            if(dx&0x80){
                oper|=2;
            }
            if(dy&0x80){
                oper|=1;
            }
            if(!oper){
                break;
            }
            x=processNumber(dx)+1;
            y=baseHeight-processNumber(dy)+this.__bottom;
            x*=scale*fontRatio;
            y*=scale;
            switch(oper){
                case 1:
                    console.warn('Scan', x,y);
                break;
                case 2:
                    path.add(new MoveTo(x,y));
                break;
                case 3:
                    path.add(new LineTo(x,y));
                break;
            }
        }
        if(counter<=0){
            console.error('死循环');
        }
        return path;
    }
}

class FontManager{
    __bgiFont={};
    __ascFontList=[];
    __hzkFont={};
    __hzkFontList=[];
    constructor(fontData){
        this.__hzkFont={};
        for(let font of fontData){
            if(/.CHR$/i.test(font.id)){
                let bgiFont=new FontBGI(font.data);
                let fontName=bgiFont.getFontName();
                this.__bgiFont[fontName]=bgiFont;
                this.__ascFontList.push({
                    label:fontName+' (BGI)',
                    value:fontName
                });
            }else if('ASCPS'==font.id){
                this.__ascFont=new FontASC(font.data);
                this.__ascFontList=this.__ascFontList.concat(font.fontNames.map((label,value)=>({
                    label,
                    value
                })));
                continue;
            }else if('HZKPST'==font.id){
                this.__hzkSymbolFont=new FontHZK(font.data,true);
                continue;
            }else {
                this.__hzkFont[font.id]=/.GBK$/i.test(font.id) ? new FontGBK(font.data) : new FontHZK(font.data);
                this.__hzkFontList.push({
                    label:font.name,
                    value:font.id
                });
            }
        }
    }
    __checkFontParam(ascFont,hzkFont){
        if(!this.__bgiFont[ascFont] && (isNaN(ascFont) || null===ascFont || ascFont<0 || ascFont>9)){
            throw new ReferenceError('西文字体必须为0-9的数字，或指定的BGI字体名称');
        }
        if(!this.__hzkFont[hzkFont]){
            throw new ReferenceError('指定的中文字体不存在');
        }
    }
    getAscFontList(){
        return this.__ascFontList.map(item=>({
            ...item
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
            if(this.__bgiFont[ascFont]){
                return this.__bgiFont[ascFont].getGlyph(code,Glyph.BASE_HEIGHT-4);
            }
            return this.__ascFont ? this.__ascFont.getGlyph(code,ascFont) : null;
        }
        
        //找到当前中文字体
        let hzkFontInstance=this.__hzkFont[hzkFont];
        if(!hzkFontInstance){
            return null;
        }

        //当前字符无法表示为GB2312或GBK
        let iconvBuf=iconv__default['default'].encode(char,'GBK');
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

exports.FontManager = FontManager;
