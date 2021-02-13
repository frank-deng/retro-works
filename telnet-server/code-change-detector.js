try{
    const watch = require('node-watch');
    if(watch && !global.__jsUpdateDetect){
        global.__jsUpdateDetect=true;
        watch(__dirname, {
            recursive: true
        }, function(event, fileName) {
            //跳过不在当前目录中的文件，非JS文件
            if('update'!=event || 0!=fileName.indexOf(__dirname) || !(/\.js$/i.test(fileName))){
                return;
            }
    
            //跳过node_modules目录中的文件
            fileNameCheck=fileName.slice(__dirname.length,fileName.length);
            if(-1!=fileNameCheck.indexOf('node_modules')){
                return;
            }
    
            //对发生变动的文件进行处理，即删除对应的require.cache，重新require该模块时新代码会生效
            if(require.cache[fileName]){
                delete require.cache[fileName];
                console.log('JS code changed:',fileName);
            }
        });
    }
}catch(e){
    console.log('Failed to load module node-watch, changes of JS files won\'t take effect without restarting the server.');
}
