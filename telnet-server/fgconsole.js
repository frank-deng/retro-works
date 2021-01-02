const axios=require('axios');
const Terminal=require('./util').Terminal;
const FGFS_HOST='http://localhost:8123/'
module.exports=class{
    data=undefined;
    constructor(stream,_exit){
        this.terminal=new Terminal(stream,{
            outputEncoding:'shift-jis'
        });
        this._exit=_exit;
        this.terminal.pc98SetBottomLine(false);
        this.terminal.clrscr();
        this.terminal.locate(0,0);
        this.terminal.setCursor(false);
        this.terminal.print('Loading...');
        this.refresh();
        this.drawFrame();
        this.refreshTimer=setInterval(()=>{
            this.refresh()
        },1000);
    }
    drawFrame(){
        this.terminal.clrscr();
        this.terminal.locate(0,1);
        this.terminal.print('飛行制御センター');
        this.terminal.locate(0,25);
        this.terminal.print('Press \'s\' to toggle sound.');
    }
    async refresh(){
        let data=null;
        try{
            data=await axios({
                method:'GET',
                url:FGFS_HOST+'/json/fgreport'
            });
        }catch(e){
            if(null!==this.data){
                this.data=null;
                this.drawFrame();
                this.terminal.locate(Math.floor((80-22)/2),12);
                this.terminal.print('飛行任務がありません。');
            }
            return;
        }

        try{
            let fgreport={};
            for(let item of data.data.children){
                fgreport[item.name]=item.value;
            }

            if(!this.data){
                this.drawFrame();
            }
            this.data=fgreport;

            this.terminal.locate(0,3);
            this.terminal.print('機種：'+fgreport.aircraft+'        ');
            this.terminal.locate(0,4);
            this.terminal.print('経度：'+fgreport['longitude-deg']+'        ');
            this.terminal.locate(0,5);
            this.terminal.print('緯度：'+fgreport['latitude-deg']+'        ');
            this.terminal.locate(0,6);
            this.terminal.print('飛行時間：'+fgreport['flight-time-string']+'        ');
            this.terminal.locate(0,7);
            this.terminal.print('残り時間：'+fgreport['ete-string']+'        ');
        }catch(e){
            console.error(e);
        }
    }
    destroy(){
        try{
            if(this.refreshTimer){
                clearInterval(this.refreshTimer);
                this.refreshTimer=null;
            }
            this.terminal.reset();
        }catch(e){
            console.error(e);
        }finally{
            this._exit();
        }
    }
    async toggleSound(){
        let {data}=await axios({
            method:'GET',
            url:FGFS_HOST+'/json/sim/sound/enabled'
        });
        await axios({
            method:'GET',
            url:FGFS_HOST+`/props/sim/sound?submit=set&enabled=${data.value ? 'false' : 'true'}`
        });
    }
    ondata(data){
        try{
            switch(data[0]){
                case 0x1b:
                    this.destroy();
                    return;
                break;
                case 0x73:
                    this.toggleSound();
                break;
            }
        }catch(e){
            console.error(e);
        }
    }
}
