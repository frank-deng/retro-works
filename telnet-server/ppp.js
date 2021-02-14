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
    constructor(stream,_exit,param){
        this._exit=_exit;
        _log('PPP server target',param.host,param.port);
        let client=net.connect({
            host:param.host,
            port:Number(param.port)
        },()=>{
            _log('PPP server connected');
            this.client=client;
            client.on('data',(data)=>{
              stream.write(data);
            });
        });
        client.on('error',()=>{
            _log('PPP server connect failed');
            this.destroy();
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
