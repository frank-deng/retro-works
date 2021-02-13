const { throws } = require('assert');
const fs = require('fs');
class Config{
    _data=null;
    _EventHandler={
        change:new Map(),
        load:new Map()
    };
    constructor(file){
        this.jsonFile=file;
        this._reload().then(()=>{
            this.$emit('load',this._data);
        });
        fs.watch(this.jsonFile,'utf8',(event)=>{
            if('change'!=event){
                return;
            }
            console.log('Configuration updated');
            this._reload();
            this.$emit('change',this._data);
        });
        console.log('Configuration initialized');
    }
    async _reload(){
        try{
            this._data=JSON.parse(await new Promise((resolve,reject)=>{
                fs.readFile(this.jsonFile,'utf8',(e,data)=>(e?reject(e):resolve(data)));
            }));
        }catch(e){
            console.error(e);
        }
    }
    get(){
        return this._data;
    }
    $on(event,handler){
        if('function'!=typeof(handler)){
            throw new TypeError('handler is not a function');
        }
        let handlerMap=this._EventHandler[event];
        if(!handlerMap){
            return;
        }
        if('load'==event && this._data){
            handler(this._data);
        }else{
            handlerMap.set(handler,true);
        }
    }
    $off(event,handler){
        if('function'!=typeof(handler)){
            throw new TypeError('handler is not a function');
        }
        let handlerMap=this._EventHandler[event];
        if(!handlerMap){
            return;
        }
        handlerMap.delete(handler);
    }
    $emit(event,param){
        let handlerMap=this._EventHandler[event];
        if(!handlerMap){
            return;
        }
        handlerMap.forEach((dummy,func)=>{
            func(this._data,param)
        });
    }
}
if(!global.config){
    global.config=new Config(process.argv[2] || './config.json');
}
module.exports=global.config;
