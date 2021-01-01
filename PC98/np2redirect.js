const net = require('net');
const crypto = require("crypto");
const _log = console.log;

const PIPE_NAME = process.argv[2];
const PIPE_PATH = `\\\\.\\pipe\\${PIPE_NAME}`;

const TARGET_HOST = process.argv[3];
const TARGET_PORT = Number(process.argv[4]);

async function readln(stream,param={}){
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
    }).then((result)=>{
        clearTimeout(timer);
        stream.write('\r\n');
        return result;
    }).catch((e)=>{
        clearTimeout(timer);
        throw e;
    });
}
class LoginManager{
    target=null;
    stream=null;
    constructor(stream){
        this.stream=stream;
        this.main();
    }
    destroy(){
    }
    async main(){
        try{
            //等待输入用户名，未输入文本时，3s后重来，输入文本后30s内不按回车则重来
            let username=null;
            while(!username){
                this.stream.write('Login:');
                username=await readln(this.stream,{
                    emptyTimeout:3,
                    inactiveTimeout:30
                });
                if(!username){
                    this.stream.write('                                        \r');
                }
            }

            //等待输入密码，30后无反应视为非法登录并要重新输入用户名
            this.stream.write('Password:');
            let password=await readln(this.stream,{
                emptyTimeout:30,
                inactiveTimeout:30,
                echo:false
            });
            if(!password){
                this.stream.write('Invalid Login.');
                this.main();
                return;
            }

            //根据用户名和密码查找对应的应用

            //Redirect everything to ppp
            this.stream.write('Success\r\n');
            let pppClient=net.connect({
                host:TARGET_HOST,
                port:TARGET_PORT
            },function(){
                _log('Remote connected');
            });
            this.stream.on('data',(data)=>{
                pppClient.write(data);
            });

            //根据返回的数据检测当前PPP连接是否需要断开
            let endStream=[0x7e,0xff,0x7d,0x23,0xc0,0x21,0x7d,0x26];
            pppClient.on('data',(data)=>{
                if(data.length > endStream.length){
                    let disconnect=true;
                    for(let i=0; i<endStream.length; i++){
                        if(data[i]!=endStream[i]){
                            disconnect=false;
                            break;
                        }
                    }
                    if(disconnect){
                        pppClient.destroy();
                        this.main();
                        return;
                    }
                }
                this.stream.write(data);
            });
            pppClient.on('error',()=>{
                _log('Remote error');
                this.main();
            });
        }catch(e){
            console.error(e);
        }
    }
}

const pipe=net.createServer((stream)=>{
    let loginManager=new LoginManager(stream);
    stream.on('end', function() {
        _log('Guest closed connection');
        loginManager.destroy();
    });
    stream.on('error', function() {
        _log('Named pipe error');
        loginManager.destroy();
    });
    _log('Guest connected');
});
pipe.on('close',function(){
    _log('Pipe: on close');
});
pipe.listen(PIPE_PATH,function(){
    _log('Pipe: '+PIPE_PATH);
});
process.on('exit', function () {
    if(client){
        client.destroy();
    }
    pipe.close();
});
