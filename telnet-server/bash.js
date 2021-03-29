const pty = require('node-pty');
const iconv = require('iconv-lite');
const _log = console.log;

module.exports=class{
  process=null;
  decodeStream=null;
  encodeStream=null;
  constructor(stream,_exit,param){
    this._exit=_exit;
    this.process=pty.spawn('/bin/bash', [], {
      cols:80,
      rows:24,
      cwd:process.env.HOME,
      env:{
        ...process.env,
        TERM:'ansi.sys',
        LANG:'zh_CN.GB2312',
        LC_CTYPE:'zh_CN.GB2312',
        LC_ALL:'zh_CN.GB2312'
      }
    })
    this.process.setEncoding('binary');
    this.process.on('data',(data)=>{
      stream.write(Buffer.from(data,'binary'));
    });
    /*
    this.encodeStream=iconv.encodeStream(param.encoding);
    this.decodeStream=iconv.decodeStream(param.encoding);
    this.process.on('data',(data)=>{
      this.encodeStream.write(data);
    });
    this.encodeStream.on('data',(data)=>{
      stream.write(data);
    });
    this.decodeStream.on('data',(data)=>{
      this.process.write(data);
    });
    */
    this.process.on('exit',()=>{
      this.process=null;
      this._exit();
    });
  }
  ondata(data){
    if(this.process){
      this.process.write(Buffer.from(data,'binary'));
    }
    /*
    if(this.process && this.decodeStream){
      this.decodeStream.write(data);
    }
    */
  }
  destroy(){
    if(this.process){
      this.process.kill();
      this.process=null;
    }
    this._exit();
  }
}
