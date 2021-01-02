const crypto = require("crypto");
const readln = require('./util').readln;
const _log = console.log;

const pppServer=require('./ppp');

module.exports=class{
    running=true;
    stream=null;
    constructor(stream){
        this.stream=stream;
        this.main();
    }
    destroy(){
        this.running=false;
    }
    async main(){
        try{
            if(!this.running){
                return false;
            }

            //等待输入用户名，未输入文本时，3s后重来，输入文本后30s内不按回车则重来
            this.stream.write('Login:');
            let username=await readln(this.stream,{
                emptyTimeout:10,
                inactiveTimeout:30
            });
            if(!username){
                this.main();
                return;
            }

            //等待输入密码，30后无反应视为非法登录并要重新输入用户名
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

            //根据用户名和密码查找对应的应用
            this.stream.write('\r\nSuccess\r\n');

            await pppServer(this.stream);
            this.main();
        }catch(e){
            console.error(e);
        }
    }
}
