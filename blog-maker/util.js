let csvParse=require('csv-parse/sync').parse;
module.exports={
  parseFile(content){
    let lines=content.split('\n');
    //Config info not found
    if(!(/^\-+$/.test(lines[0].trim()))){
      return [content,{}];
    }

    //Remove first line
    lines.shift();

    //Get config info
    let configLine=[];
    while(lines.length){
      let line=lines.shift().trim();
      if(/^\-+$/.test(line)){
        break;
      }
      configLine.push(line);
    }
    
    //Generate final content
    let contentFinal=lines.join('\n');

    //Parse configs
    let config={};
    for(let line of configLine){
      let lineSplit=line.split(':');
      let key=lineSplit[0].trim(), value=lineSplit.slice(1,lineSplit.length).join(':').trim();
      if(/^\".*\"$/.test(value)){
        value=csvParse(value,{
          trim:true
        })[0][0];
      }else if(/^\[.*\]$/.test(value)){
        value=csvParse(value.slice(1,value.length-1),{
          trim:true
        })[0];
      }
      config[key]=value;
    }

    return [contentFinal, config];
  }
}
