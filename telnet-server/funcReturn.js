const Terminal=require('./util').Terminal;
const LanguagePack=require('./util').LanguagePack;

function funcReturn(throwError=false,returnFromTry=false,returnFromCatch=false,returnFromFinally=false){
  try{
    if(throwError){
      throw new Error('InternalUse'); 
    }
    if(returnFromTry){
      return 'try';
    }
  }catch(e){
    if('InternalUse'!=e.message){
      console.error(e);
    }
    if(returnFromCatch){
      return 'catch';
    }
  }finally{
    if(returnFromFinally){
      return 'finally';
    }
  }
  return 'outside';
}

function combinations(values,count,callback){
  if(!Array.isArray(values)){
    throw new TypeError('values must be an array.');
  }
  if('function'!=typeof(callback)){
    throw new TypeError('callback must be a function.');
  }

  //先循环4层吧
  for(let v0 of values){
    for(let v1 of values){
      for(let v2 of values){
        for(let v3 of values){
          callback([v0,v1,v2,v3]);
        }
      }
    }
  }
}

module.exports=class{
  constructor(stream,_exit,param={}){
    this._exit=_exit;
    this.terminal=new Terminal(stream,{
      outputEncoding:param.encoding
    });
    this.terminal.clrscr();
    this.terminal.locate(0,0);
    this.terminal.setcursor(false);
    this.drawMain();
  }
  drawMain(){
    //Print table header
    this.terminal.locate(1,2);
    this.terminal.print('Throw Error');
    this.terminal.locate(13,2);
    this.terminal.print('try');
    this.terminal.locate(17,2);
    this.terminal.print('catch');
    this.terminal.locate(24,2);
    this.terminal.print('finally');
    this.terminal.locate(40,2);
    this.terminal.print('Return from');
    let row=3;
    combinations([false,true],4,(values)=>{
      let [throwError,returnFromTry,returnFromCatch,returnFromFinally]=values;

      //print table content
      this.terminal.locate(1,row);
      this.terminal.print(throwError ? 'Yes' : 'No');
      this.terminal.locate(13,row);
      this.terminal.print(returnFromTry ? 'Yes' : 'No');
      this.terminal.locate(17,row);
      this.terminal.print(returnFromCatch ? 'Yes' : 'No');
      this.terminal.locate(24,row);
      this.terminal.print(returnFromFinally ? 'Yes' : 'No');
      this.terminal.locate(40,row);

      let result=funcReturn(throwError,returnFromTry,returnFromCatch,returnFromFinally);
      switch(result){
        case 'outside':
          this.terminal.print('Outside');
        break;
        default:
          this.terminal.print(result);
        break;
      }
      row++;
    });

    this.terminal.locate(1,24);
    this.terminal.print('Press Esc key to exit.');
  }
  destroy(){
    this._exit();
  }
  ondata(data){
    try{
      switch(data[0]){
        case 0x1b:
          this.terminal.reset();
          this.destroy();
          return;
        break;
      }
    }catch(e){
      console.error(e);
    }
  }
}

