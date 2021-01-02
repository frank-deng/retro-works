module.exports=class{
    constructor(stream,_exit){
        this.stream=stream;
        this._exit=_exit;
    }
    ondata(data){
        try{
            console.log(data,data[0],data[0].toString(16));
            this.stream.write('>');
            for(let value of data){
                this.stream.write(' '+value.toString(16));
            }
            this.stream.write('\r\n');
            if(0x1b==data[0]){
                this.stream.write('Exit.\r\n');
                this._exit();
            }
        }catch(e){
            console.error(e);
            this._exit();
        }
    }
}
