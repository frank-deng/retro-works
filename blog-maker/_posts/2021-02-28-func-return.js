const TARGET_FILE='2021-02-28-func-return.md';
const fs=require('fs');

function funcReturn(throwError=false,returnFromTry=false,returnFromCatch=false,returnFromFinally=false){
  let execSeq=[];
  try{
    execSeq.push('try');
    if(throwError){
      throw new Error('InternalUse'); 
    }
    if(returnFromTry){
      return {
        execSeq,
        from:'try'
      };
    }
  }catch(e){
    if('InternalUse'!=e.message){
      console.error(e);
    }
    execSeq.push('catch');
    if(returnFromCatch){
      return {
        execSeq,
        from:'catch'
      };
    }
  }finally{
    execSeq.push('finally');
    if(returnFromFinally){
      return {
        execSeq,
        from:'finally'
      };
    }
  }
  execSeq.push('finally之后的代码');
  return {
    execSeq,
    from:'finally之后'
  };
}

fs.writeFileSync(TARGET_FILE,
`---
layout: post
title: JavaScript中try、catch、finally块中的return的处理方式
tags: [JavaScript]
---

当\`try\`块未捕获异常时，以下表格归纳了\`return\`语句在\`try\`块、\`finally\`块、\`finally\`块之后的代码时，会使用哪个代码块里的return：
`)


fs.appendFileSync(TARGET_FILE,`
|\`try\`块return|\`finally\`块return|执行顺序|\`return\`对应的代码块|
|-----|-----|-----|-----|
`);

let values=[false,true];
for(let returnFromTry of values){
  for(let returnFromFinally of values){
    let result=funcReturn(false,returnFromTry,true,returnFromFinally);
    fs.appendFileSync(TARGET_FILE,
      `|${returnFromTry?'是':'否'}|${returnFromFinally?'是':'否'}|${result.execSeq.join('→')}|${result.from}|\n`
    );
  }
}

fs.appendFileSync(TARGET_FILE,`
当\`try\`块捕获到异常时，以下表格归纳了\`return\`语句在\`catch\`块、\`finally\`块、\`finally\`块之后的代码时，会使用哪个代码块里的return：
`)

fs.appendFileSync(TARGET_FILE,`
|\`catch\`块return|\`finally\`块return|执行顺序|\`return\`对应的代码块|
|-----|-----|-----|-----|
`);

for(let returnFromCatch of values){
  for(let returnFromFinally of values){
    let result=funcReturn(true,true,returnFromCatch,returnFromFinally);
    fs.appendFileSync(TARGET_FILE,
      `|${returnFromCatch?'是':'否'}|${returnFromFinally?'是':'否'}|${result.execSeq.join('→')}|${result.from}|\n`
    );
  }
}

