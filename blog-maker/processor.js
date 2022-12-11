const Markdown=require('markdown-it')({
  html:true
});
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
const svg = new SVG({
  mtextFont: $_CONFIG.mathFont,
  fontCache:'none',
  internalSpeechTitles:false
});
require('mathjax-full/js/util/entities/all.js');

function svg2gif(svgData){
  return new Promise((resolve,reject)=>{
    let convert=spawn('magick',['convert','-','+dither','+antialias','-colors','16','GIF:-']);
    let result=Buffer.alloc(0,0,'binary');
    convert.stdout.on('data',(data)=>{
      result=Buffer.concat([result,data]);
    });
    convert.stderr.on('data',(data)=>{
      console.error('convert:',data.toString());
    });
    convert.stdin.write(svgData);
    convert.stdin.end();
    convert.on('close',()=>{
      resolve(result);
    });
  });
}
function applyFont(document,text,fontTable={}){
  let _apply=(text,charType)=>{
    let node;
    if(fontTable[charType]){
      node=document.createElement('font');
      node.setAttribute('face', fontTable[charType]);
      node.appendChild(document.createTextNode(textProc));
    }else{
      node=document.createTextNode(textProc);
    }
    return node;
  }

  let textProc='', lastCharType=null, result=document.createDocumentFragment();
  for(let i=0; i<text.length; i++){
    let ch=text[i], charCode=text.charCodeAt(i), charType=null;
    if(charCode>=0x20 && charCode <= 0x7f){
      charType='ascii';
    }else if(charCode>0x7f){
      charType='cjk';
    }else{
      charType=null;
    }

    if(charType==lastCharType){
      textProc+=ch;
      continue;
    }else if(!textProc.length){
      textProc+=ch;
      lastCharType=charType;
      continue;
    }

    result.appendChild(_apply(textProc, lastCharType));

    textProc=ch;
    lastCharType=charType;
  }
  if(textProc){
    result.appendChild(_apply(textProc, lastCharType));
  }
  return result;
}
function processTitle(title,params={}){
  var dom=new JSDOM();
  var document=dom.window.document;
  document.body.appendChild(applyFont(document,title,params.font));
  return document.body.innerHTML;
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

    //Convert Chinese characters to its correcct glyph
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

  //Walk through the whole dom
  let tagNameBlacklist={
    'CODE':true,
    'PRE':true,
    'IMG':true,
    'BR':true
  };
  let _procDom=(nodeList)=>{
    let nodeListCopy=[];
    for(let item of nodeList){
      nodeListCopy.push(item);
    }
    for(let node of nodeListCopy){
      if(tagNameBlacklist[node.tagName]){
        continue;
      }

      //Process child nodes
      if(1==node.nodeType){
        _procDom(node.childNodes);
        continue;
      }

      //Replace child node with font applied
      if(3==node.nodeType){
        node.parentNode.replaceChild(applyFont(document, node.nodeValue, params.font),node);
      }
    }
  }
  _procDom(document.body.childNodes);

  //Add template
  let html=document.body.innerHTML;
  if(params.template){
    html=await new Promise((resolve,reject)=>{
      ejs.renderFile(params.template,{
        encoding:params.targetEncoding,
        title:params.title,
        titleProcessed:processTitle(params.title,params),
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

