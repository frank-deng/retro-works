const Terminal=require('./util').Terminal;
module.exports=class{
    constructor(stream,_exit){
        this.terminal=new Terminal(stream,{
            outputEncoding:'shift-jis'
        });
        this._exit=_exit;
        this.terminal.pc98SetBottomLine(false);
        this.terminal.clrscr();
        this.terminal.locate(0,0);
        this.terminal.print('飛行任務がありません。');
    }
    destroy(){
        this.terminal.pc98SetBottomLine(true);
        this.terminal.clrscr();
        this._exit();
    }
    ondata(data){
        try{
            if(0x1b==data[0]){
                this.destroy();
            }
        }catch(e){
            console.error(e);
        }
    }
}
