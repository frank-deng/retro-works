const net = require('net');

const PIPE_NAME = process.argv[2];
const TARGET_HOST = process.argv[3];
const TARGET_PORT = Number(process.argv[4]);


const PIPE_PATH = `\\\\.\\pipe\\${PIPE_NAME}`;

const _log = console.log;
function _logbuf(value){
    if(value>=0x20 && value<0x7f){
        return String.fromCharCode(value);
    }
    return value;
}

var pipe,stream,client,targetBuffer=[];clientBuffer=[],buf=Buffer.alloc(1);

function sendTarget(){
  if(!targetBuffer.length){
    return;
  }
  setImmediate(sendTarget);
  if(client){
    buf[0]=targetBuffer.shift();
    client.write(buf);
  }
}
function sendClient(){
  if(!clientBuffer.length){
    return;
  }
  setImmediate(sendClient);
  if(stream){
    buf[0]=clientBuffer.shift();
    stream.write(buf);
  }
}
sendClient();
pipe=net.createServer((_stream)=>{
    client=net.connect({
        host:TARGET_HOST,
        port:TARGET_PORT
    },function(){
        _log('Remote connected');
    });
    stream=_stream;
    stream.on('data',(s)=>{
        if(!targetBuffer.length){
            setImmediate(sendTarget);
        }
        let len=s.length;
        for(let i=0; i<len; i++){
            targetBuffer.push(s[i]);
        }
    });
    client.on('data',(s)=>{
        if(!clientBuffer.length){
            setImmediate(sendClient);
        }
        let len=s.length;
        for(let i=0; i<len; i++){
            clientBuffer.push(s[i]);
        }
    });
    stream.on('end', function() {
        _log('Guest closed connection');
        client.destroy();
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
