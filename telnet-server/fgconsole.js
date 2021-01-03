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
        this.terminal.setcursor(false);
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
        this.terminal.setattr(46);
        for(let i=0;i<80;i++){
            this.terminal.print(' ');
        }
        this.terminal.locate(Math.round((80-16)/2),1);
        this.terminal.print('飛行制御センター');
        
        this.terminal.locate(0,25);
        this.terminal.setattr(46);
        for(let i=0;i<80;i++){
            this.terminal.print(' ');
        }
        this.terminal.locate(2,25);
        this.terminal.print('Esc：終了    s:ｻｳﾝﾄﾞｵﾝ/ｵﾌ    p:一時停止/再開');
        this.terminal.setattr(0);

        //this.terminal.locate(0,25);
        //this.terminal.print('Press \'s\' to toggle sound.');
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
            fgreport['longitude'] = Math.abs(fgreport['longitude-deg']).toFixed(6)+(fgreport['longitude-deg']>=0 ? 'E' : 'W');
            fgreport['latitude'] = Math.abs(fgreport['latitude-deg']).toFixed(6)+(fgreport['latitude-deg']>=0 ? 'N' : 'S');
            this.terminal.locate(0,3);
            this.terminal.print('機種：    '+fgreport.aircraft+'        ');
            this.terminal.locate(0,4);
            this.terminal.print('経度：    '+fgreport['longitude']+'        ');
            this.terminal.locate(0,5);
            this.terminal.print('緯度：    '+fgreport['latitude']+'        ');
            this.terminal.locate(0,6);
            this.terminal.print('飛行時間：'+fgreport['flight-time-string']+'        ');
            this.terminal.locate(0,7);
            this.terminal.print('残り時間：'+fgreport['ete-string']+'        ');
            this.terminal.locate(0,8);
            this.terminal.print('総距離：  '+fgreport['total-distance'].toFixed(1)+'nm        ');
            this.terminal.locate(0,9);
            this.terminal.print('残り距離：'+fgreport['distance-remaining-nm'].toFixed(1)+'nm        ');
            this.terminal.locate(0,10);
            this.terminal.print('飛行距離：'+(Number(fgreport['total-distance'])-Number(fgreport['distance-remaining-nm'])).toFixed(1)+'nm        ');

            this.terminal.locate(0,24);
            if(fgreport['crashed']){
                this.terminal.setattr(5,41);
                this.terminal.print('墜落しました');
            }else if(fgreport['paused']){
                this.terminal.setattr(21);
                this.terminal.print('一時停止');
            }else{
                this.terminal.setattr(20);
                this.terminal.print('飛行中');
            }
            this.terminal.setattr(0);
            this.terminal.print('                ');
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
    async togglePause(){
        await axios({
            method:'GET',
            url:FGFS_HOST+'/run.cgi?value=pause'
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
                case 0x70:
                    this.togglePause();
                break;
            }
        }catch(e){
            console.error(e);
        }
    }
}
