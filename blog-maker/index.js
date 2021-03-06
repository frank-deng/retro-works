const processDocument=require('./processor');
const fs=require('fs');
const rimraf=require('rimraf');
const ncp=require('ncp').ncp;
const ejs=require('ejs');
const iconv=require('iconv-lite');
const parseFile=require('./util').parseFile;

var config={
  "staticDir":"static",
  "sourceDir":"_posts",
  "sourceEncoding":"UTF-8",
  "target":"dist",
  "imageDir":"images",
  "templateDir":"template",
  "layout":"post",
  "index":"index",
  "equationDir":"equation"
};

async function getMasterConfig(){
  let configFile=await new Promise((resolve,reject)=>{
    fs.readFile(`${__dirname}/config.json`,'UTF-8',(e,data)=>(e?reject(e):resolve(data)));
  });
  Object.assign(config,JSON.parse(configFile));
  return config;
}
async function processPost(name,idx){
  //Read content
  let [content,localConfig]=parseFile(await new Promise((resolve,reject)=>{
    fs.readFile(`${__dirname}/${config.sourceDir}/${name}.md`,config.sourceEncoding,(e,data)=>(e?reject(e):resolve(data)));
  }));

  //Get template
  let template=(localConfig.layout || config.layout);
  if(template){
    template=__dirname+'/'+config.templateDir+'/'+template+'.tpl';
  }

  //Process document
  let result=await processDocument(content,{
    imagePrefix:config.equationDir+`/p${idx}`,
    targetEncoding:config.targetEncoding,
    template,
    title: (localConfig.title || name),
    scale: (localConfig.scale || config.scale),
    font: (config.font||{})
  });

  //Generate filename
  let fileName=`p${idx}.htm`;

  //Write to the target
  let target=config.target;
  await Promise.all([
    new Promise((resolve,reject)=>{
      fs.writeFile(target+'/'+fileName,result.html,'binary',(e)=>(e?reject(e):resolve(e)));
    }),
    ...result.image.map(item=>new Promise((resolve,reject)=>{
      fs.writeFile(target+'/'+item.path,item.data,'binary',(e)=>(e?reject(e):resolve(e)));
    }))
  ]);

  //Output title
  return {
    title:(localConfig.title || name),
    link:fileName,
    tags:localConfig.tags
  };
}
async function main(){
  //Get master config
  getMasterConfig();
  let target=config.target;

  //Clear and recreate destination folder structure
  await new Promise((r)=>{
    rimraf(target,r);
  });
  await Promise.all([
    new Promise((resolve,reject)=>{
      fs.mkdir(target+'/'+config.imageDir,{
        recursive:true
      },(e)=>(e?reject(e):resolve(e)));
    }),
    new Promise((resolve,reject)=>{
      fs.mkdir(target+'/'+config.equationDir,{
        recursive:true
      },(e)=>(e?reject(e):resolve(e)));
    }),
    new Promise((resolve,reject)=>{
      ncp(__dirname+'/'+config.staticDir, target+'/'+config.staticDir, (e)=>(e?reject(e):resolve(e)));
    })
  ]);

  //Get all the posts
  let posts = await new Promise((resolve,reject)=>{
    fs.readdir(__dirname+'/'+config.sourceDir,(err,files)=>{
      if(err){
        reject(err);
      }
      let fileList=files.filter(file=>'md'==file.split('.').pop()).map(file=>{
        let fileSplit=file.split('.');
        return fileSplit.slice(0,fileSplit.length-1).join('.');
      });
      fileList.reverse();
      resolve(fileList);
    });
  });

  //Process all the posts
  let postList=await Promise.all(posts.map((postName,idx)=>processPost(postName,idx)));

  //Generate index page
  let indexPage = await new Promise((resolve,reject)=>{
    let template=__dirname+'/'+config.templateDir+'/'+config.index+'.tpl';
    ejs.renderFile(template,{
      encoding:config.targetEncoding,
      postList
    },(e,data)=>(e?reject(e):resolve(data)));
  });
  if(config.targetEncoding){
    indexPage=iconv.encode(indexPage,config.targetEncoding);
  }
  await new Promise((resolve,reject)=>{
    fs.writeFile(target+`/index.htm`,
      indexPage,
      'binary',(e)=>(e?reject(e):resolve(e)));
  });
}

try{
  main().catch((e)=>{
    console.error(e);
  });
}catch(e){
  console.error(e);
}

