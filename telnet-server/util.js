const iconv=require('iconv-lite');

class Terminal{
	static strlen(str){
		let len=str.length, result=0;
		for(let i=0; i<len; i++){
			let c=str.charCodeAt(i);
			if((c>=0x4e00 && c<=0x9fa5) || (c>=0xf900 && c<=0xfa2d)){
				result++;
            }
            result++;
        }
        return result;
    }
    static lpad(str,size,padchar=' '){
        let len=Terminal.strlen(str), result=str;
        if(len<size){
            result=padchar.repeat(size-len)+result;
        }
        return result;
    }
    static rpad(str,size,padchar=' '){
        let len=Terminal.strlen(str), result=str;
        if(len<size){
            result+=padchar.repeat(size-len);
        }
        return result;
    }
    constructor(stream, param={}){
        this.stream=stream;
        this.outputEncoding=param.outputEncoding;
    }
    print(data){
        let dataOutput=data;
        if('string'==typeof(data) && this.outputEncoding){
            dataOutput=iconv.encode(dataOutput,this.outputEncoding);
        }
        this.stream.write(dataOutput);
    }
    locate(x,y){
        this.stream.write(`\x1b[${Math.round(y)};${Math.round(x)}H`);
    }
    clrscr(){
        this.stream.write('\x1b[2J');
    }
    clrline(){
        this.stream.write('\x1b[0K\x1b[1K');
    }
    setcursor(enable){
        this.stream.write(enable ? '\x1b[>5l' : '\x1b[>5h');
    }
    setattr(){
        let attrs=[];
        for(let i=0; i<arguments.length; i++){
            attrs.push(arguments[i]);
        }
        this.stream.write('\x1b['+attrs.join(';')+'m');
    }
    pc98SetBottomLine(enable){
        this.stream.write(enable ? '\x1b[>1l' : '\x1b[>1h');
    }
    reset(){
        this.clrscr();
        this.pc98SetBottomLine(true);
        this.setcursor(true);
        this.setattr(0);
        this.locate(0,0);
    }
}
function readln(stream,param={}){
    var inputHandler=null;
    let echo=param.hasOwnProperty('echo') ? param.echo : true;
    let timer=null, buffer='', charBlacklist={
        '\x09':true
    };
    return new Promise((resolve)=>{
        const setAbortTimeout=(timeout)=>{
            if(timer){
                clearTimeout(timer);
            }
            if(!timeout){
                return;
            }
            timer=setTimeout(()=>{
                stream.off('data',inputHandler);
                resolve('');
            },timeout*1000);
        }
        inputHandler=(data)=>{
            setAbortTimeout(param.inactiveTimeout);
            for(let char of data.toString()){
                if('\r'==char || '\n'==char){
                    stream.off('data',inputHandler);
                    resolve(buffer);
                    return;
                }else if('\x08'==char){
                    if(buffer.length){
                        buffer=buffer.slice(0,buffer.length-1);
                        echo && stream.write('\x08 \x08');
                    }
                }else if(!charBlacklist[char]){
                    echo && stream.write(char);
                    buffer+=char;
                }
            }
        }
        stream.on('data',inputHandler);
        setAbortTimeout(param.emptyTimeout);
    }).finally(()=>{
        clearTimeout(timer);
    });
}
class LanguagePack{
	_lang={};
	_currentLang='en';
	constructor(data,defaultLang='en'){
		this._lang=data;
		this._currentLang=defaultLang
    }
    setLanguage(lang){
        this._currentLang=lang;
    }
    t(key,language=null){
        try{
            let data=this._lang[language || this._currentLang];
            if(!data){
                return key;
            }
            return data[key];
        }catch(e){
            console.error(e);
        }
        return key;
    }
    get(key,language=null){
        return this.t(key,language);
    }
}
module.exports={
    readln,
    Terminal,
    LanguagePack
}