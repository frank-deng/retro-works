const pty = require('node-pty');
const iconv = require('iconv-lite');
const _log = console.log;
const STRING_RAW_MODE_ON='\x1b[>rl';
const STRING_RAW_MODE_OFF='\x1b[>rh';

module.exports=class{
  process=null;
  decodeStream=null;
  encodeStream=null;
  rawMode=false;
  constructor(stream,_exit,param){
    this._exit=_exit;
    this.process=pty.spawn('/bin/bash', [], {
      cols:80,
      rows:24,
      cwd:process.env.HOME,
      env:{
        ...process.env,
        TERM:'ansi.sys'
      }
    });
    this.process.setEncoding('utf8');
    this.process.on('data',(data)=>{
      if(0==data.indexOf(STRING_RAW_MODE_ON)){
        this.process.setEncoding('binary');
        this.rawMode=true;
      }else if(0==data.indexOf(STRING_RAW_MODE_OFF)){
        this.process.setEncoding('utf8');
        this.rawMode=false;
      }
      if(this.rawMode){
        stream.write(Buffer.from(data,'binary'));
      }else{
        this.encodeStream.write(data);
      }
    });
    this.encodeStream=iconv.encodeStream(param.encoding);
    this.decodeStream=iconv.decodeStream(param.encoding);
    this.encodeStream.on('data',(data)=>{
      stream.write(data);
    });
    this.decodeStream.on('data',(data)=>{
      this.process.write(data);
    });
    this.process.on('exit',()=>{
      this.process=null;
      this._exit();
    });
  }
  ondata(data){
    if(!this.process){
      return;
    }
    if(this.rawMode){
      this.process.write(Buffer.from(data,'binary'));
    }else if(this.decodeStream){
      this.decodeStream.write(data);
    }
  }
  destroy(){
    if(this.process){
      this.process.kill();
      this.process=null;
    }
    this._exit();
  }
}
