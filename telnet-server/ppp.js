const net = require('net');
const TARGET_HOST = process.argv[3];
const TARGET_PORT = Number(process.argv[4]);
const _log = console.log;

//根据返回的数据检测当前PPP连接是否需要断开
function checkDisconnect(data){
    let endStream=[0x7e,0xff,0x7d,0x23,0xc0,0x21,0x7d,0x26];
    if(data.length < endStream.length){
        return false;
    }
    for(let i=0; i<endStream.length; i++){
        if(data[i]!=endStream[i]){
            return false;
        }
    }
    return true;
}
module.exports=class{
    client=null;
    constructor(stream,_exit){
        this._exit=_exit;
        let client=net.connect({
            host:TARGET_HOST,
            port:TARGET_PORT
        },()=>{
            _log('PPP server connected');
            this.client=client;
            client.on('data',(data)=>{
                if(checkDisconnect(data)){
                    _log('PPP server disconnected');
                    this.destroy();
                }else{
                    stream.write(data);
                }
            });
            client.on('error',()=>{
                this.destroy();
            });
        });
    }
    ondata(data){
        if(this.client){
            this.client.write(data);
        }
    }
    destroy(){
        if(this.client){
            this.client.destroy();
        }
        this._exit();
    }
}
