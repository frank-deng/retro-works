const net = require('net');

const PIPE_NAME = process.argv[2];
const TARGET_HOST = process.argv[3];
const TARGET_PORT = Number(process.argv[4]);


const PIPE_PATH = `\\\\.\\pipe\\${PIPE_NAME}`;

const _log = console.log;
var pipe,stream,client;
pipe=net.createServer((_stream)=>{
    client=net.connect({
        host:TARGET_HOST,
        port:TARGET_PORT
    },function(){
        _log('Remote connected');
    });
    stream=_stream;
    stream.pipe(client);
    client.pipe(stream);
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
