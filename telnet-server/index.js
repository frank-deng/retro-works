const net = require('net');
const _log = console.log;

const LoginManager=require('./login');

const PIPE_NAME = process.argv[2];
const PIPE_PATH = `\\\\.\\pipe\\${PIPE_NAME}`;

const pipe=net.createServer((stream)=>{
    _log('Guest connected');
    let loginManager=new LoginManager(stream);
    stream.on('end', function() {
        _log('Guest closed connection');
        loginManager.destroy();
    });
    stream.on('error', function(e) {
        _log('Named pipe error',e);
        loginManager.destroy();
    });
});
pipe.on('close',function(){
    _log('Pipe: on close');
});
pipe.listen(PIPE_PATH,function(){
    _log('Pipe: '+PIPE_PATH);
});
process.on('exit', function () {
    pipe.close();
});
