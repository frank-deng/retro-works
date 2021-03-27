const crypto = require("crypto");
const fs = require('fs');
const config=require('./config');
const readln = require('./util').readln;
const _log = console.log;

class UserManager{
    _data={};
    constructor(file){
        this.jsonFile=file;
        config.$on('load',()=>{
            try{
                this._reload();
            }catch(e){
                console.error(e);
            }
        });
        config.$on('change',()=>{
            try{
                this._reload();
                _log('login info updated');
            }catch(e){
                console.error(e);
            }
        });
    }
    async _reload(){
        try{
            this._data={};
            if(!config.get()){
                return;
            }
            let data=config.get().login;
            for(let username in data){
                let userData=data[username];
                this._data[username]={
                    username,
                    password:userData.password,
                    module:userData.module,
                    param:userData.param
                };
            }
        }catch(e){
            console.error(e);
        }
    }
    get(username){
        return this._data[username];
    }
}
const userManager=new UserManager('./login.json');

module.exports=class{
    running=true;
    stream=null;
    instance=null;
    _sendData=(data)=>{
        try{
            this.instance.ondata(data);
        }catch(e){
            console.error(e);
        }
    }
    constructor(stream){
        this.stream=stream;
        this.main();
    }
    destroy(){
        this.running=false;
        if(this.instance && 'function'==typeof(this.instance.destroy)){
            this.instance.destroy();
            this.instance=null;
        }
    }
    async main(){
        try{
            if(!this.running){
                return false;
            }

            await new Promise((_continue)=>{
                setTimeout(_continue, 500);
            });

            //等待输入用户名，未输入文本时，3s后重来，输入文本后30s内不按回车则重来
            this.stream.write('\r\nLogin:');
            let username=await readln(this.stream,{
                emptyTimeout:30,
                inactiveTimeout:30
            });
            if(!username){
                this.main();
                return;
            }

            //等待输入密码，30s后无反应视为非法登录并要重新输入用户名
            this.stream.write('\r\nPassword:');
            let password=await readln(this.stream,{
                emptyTimeout:30,
                inactiveTimeout:30,
                echo:false
            });
            if(!password){
                this.stream.write('\r\nInvalid Login.\r\n');
                this.main();
                return;
            }

            //将密码用sha256处理后，根据用户名和密码查找对应的应用
            let passwordHash=crypto.createHash('sha256').update(password).digest('hex');
            let loginInfo=userManager.get(username);
            if(!loginInfo || passwordHash!=loginInfo.password){
                this.stream.write('\r\nInvalid Login.\r\n');
                setTimeout(()=>{
                  this.main();
                },2000); //防止密码被暴力破解试出来
                return;
            }

            //运行该用户对应的程序
            this.stream.write('\r\nSuccess\r\n');
            await new Promise((_exit)=>{
                try{
                    this.instance=new (require(loginInfo.module))(this.stream,_exit,loginInfo.param);
                    if('function'==typeof(this.instance.ondata)){
                        this.stream.on('data',this._sendData);
                    }
                }catch(e){
                    console.error(e);
                    this.stream.write('Failed to start application.\r\n');
                    _exit();
                }
            });
            this.stream.off('data',this._sendData);
            this.main();
        }catch(e){
            console.error(e);
        }
    }
}
