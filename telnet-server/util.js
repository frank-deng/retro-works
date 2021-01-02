module.exports={
    readln:function(stream,param={}){
        var inputHandler=null;
        let echo=param.hasOwnProperty('echo') ? param.echo : true;
        let timer=null, buffer='', charBlacklist={
            '\x09':true
        };
        return new Promise((resolve)=>{
            const setAbortTimeout=(timeout)=>{
                if(timer){
                    clearTimeout(timer);
                }
                if(!timeout){
                    return;
                }
                timer=setTimeout(()=>{
                    stream.off('data',inputHandler);
                    resolve('');
                },timeout*1000);
            }
            inputHandler=(data)=>{
                setAbortTimeout(param.inactiveTimeout);
                for(let char of data.toString()){
                    if('\r'==char || '\n'==char){
                        stream.off('data',inputHandler);
                        resolve(buffer);
                        return;
                    }else if('\x08'==char){
                        if(buffer.length){
                            buffer=buffer.slice(0,buffer.length-1);
                            echo && stream.write('\x08 \x08');
                        }
                    }else if(!charBlacklist[char]){
                        echo && stream.write(char);
                        buffer+=char;
                    }
                }
            }
            stream.on('data',inputHandler);
            setAbortTimeout(param.emptyTimeout);
        }).finally(()=>{
            clearTimeout(timer);
        });
    }
}
