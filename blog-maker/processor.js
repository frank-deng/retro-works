const Markdown=require('markdown-it')();
const JSDOM=require('jsdom').JSDOM;
const ejs=require('ejs');
const iconv=require('iconv-lite');

//Tools for calling imagemagick convert
const util = require('util');
const spawn = require('child_process').spawn;

//MathJAX init
const mathjax = require('mathjax-full/js/mathjax.js').mathjax;
const TeX = require('mathjax-full/js/input/tex.js').TeX;
const SVG = require('mathjax-full/js/output/svg.js').SVG;
const liteAdaptor = require('mathjax-full/js/adaptors/liteAdaptor.js').liteAdaptor;
const RegisterHTMLHandler = require('mathjax-full/js/handlers/html.js').RegisterHTMLHandler;
const adaptor = liteAdaptor({
  fontSize:16
});
RegisterHTMLHandler(adaptor);

const tex = new TeX({packages:require('mathjax-full/js/input/tex/AllPackages.js').AllPackages});
const svg = new SVG({fontCache:'none', internalSpeechTitles:false});

function svg2gif(svgData){
  return new Promise((resolve,reject)=>{
    let convert=spawn('convert',['-background','white','-','+antialias','GIF:-']);
    let errorMsg='', result=Buffer.alloc(0,0,'binary');
    convert.stderr.on('data', function(data){
      errorMsg+=data;
    });
    convert.stdout.setEncoding('binary');
    convert.stdout.on('data',(data)=>{
      result=Buffer.concat([result,Buffer.from(data,'binary')]);
    });
    convert.on('exit',(code)=>{
      if(code){
        reject(errorMsg);
        return;
      }
      resolve(result);
    });
    convert.stdin.write(svgData);
    convert.stdin.end();
  });
}
async function processHTML(content,params={}){
  //Replace equations with corresponding images
  var dom=new JSDOM(content);
  var document=dom.window.document;
  var containers=document.querySelectorAll('mjx-container');

  let svgList=[];
  for(let item of containers){
    //Get svg data
    let svg=item.querySelector('svg');
    let width=parseFloat(svg.getAttribute('width'));
    let height=parseFloat(svg.getAttribute('height'));
    let scale=params.scale || 16;
    svg.setAttribute('width',`${width*scale}px`);
    svg.setAttribute('height',`${height*scale}px`);
    let svgContent='<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'+item.innerHTML;
    
    //Replace svg with image tag
    let img=document.createElement('img');
    let imgPath=`${params.imagePrefix||''}e${svgList.length}.gif`;
    img.setAttribute('src',imgPath);
    img.setAttribute('valign','middle');
    img.setAttribute('align','center');
    item.parentNode.replaceChild(img,item);

    //Prepare data for conversion
    svgList.push({
      path:imgPath,
      data:svgContent
    });
  }

  let imgList=[];
  for(let item of svgList){
    imgList.push({
      ...item,
      data:await svg2gif(item.data)
    });
  }
  /*
  let resp=await Promise.all(svgList.map(item=>svg2gif(item.data)));
  let len=resp.length, imgList=[];
  for(let i=0; i<len; i++){
    imgList.push({
      ...svgList[i],
      data:resp[i]
    });
  }
  */

  //Add template
  let html=document.body.innerHTML;
  if(params.template){
    html=await new Promise((resolve,reject)=>{
      ejs.renderFile(params.template,{
        encoding:params.targetEncoding,
        title:params.title,
        content:html
      },(e,data)=>(e?reject(e):resolve(data)));
    });
  }
  return {
    html:params.targetEncoding ? iconv.encode(html,params.targetEncoding) : html,
    image:imgList
  };
}
module.exports=async function(content,params={}){
  var contentHTML=Markdown.render(content);
  var html = mathjax.document(contentHTML, {InputJax: tex, OutputJax: svg});
  html.render();
  return await processHTML(adaptor.outerHTML(adaptor.root(html.document)),{
    ...params
  });
}

