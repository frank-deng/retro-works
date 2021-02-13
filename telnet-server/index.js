require('./code-change-detector');
const config=require('./config');
const net = require('net');
const LoginManager=require('./login');

const _log = console.log;
config.$on('load',function(conf){
    if(conf.pipeName){
        const PIPE_PATH = `\\\\.\\pipe\\${config.get().pipeName}`;
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
    }
    if(conf.tcpServer){
        const server=net.createServer();
        server.on('connection', function(socket) {
            _log('Guest connected TCP');
            let loginManager=new LoginManager(socket);
            socket.on('end', function() {
                _log('Guest closed connection TCP');
                loginManager.destroy();
            });
            socket.on('error', function(e) {
                _log('TCP server error',e);
                loginManager.destroy();
            });
        });
        server.listen(conf.tcpServer.port, function() {
            console.log(`Server: ${conf.tcpServer.port}`);
        });
        process.on('exit', function () {
            server.close();
        });
    }
});
