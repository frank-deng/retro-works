#!/usr/bin/env node
const processDocument=require('./processor');
const parseFile=require('./util').parseFile;
const prettify = require('html-prettify');
const fs=require('fs');
let [content,localConfig]=parseFile(fs.readFileSync(process.argv[process.argv.length-1], 'utf-8'));
processDocument(content).then((resp)=>{
  console.log(prettify(resp.html));
});
