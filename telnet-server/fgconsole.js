const fecha=require('fecha');
const axios=require('axios');
const Terminal=require('./util').Terminal;
const LanguagePack=require('./util').LanguagePack;
const LANGUAGE_PACK_DATA={
	'zh-cn':{
		'Flight Control Center':'飞控中心',
		'Loading':'加载中……',
        KEYBOARD_HELP_IDLE:'Esc：退出',
		KEYBOARD_HELP:'Esc：退出    s：开启/关闭声音    p：暂停/继续',
		'No Flight Mission':'没有飞行任务。',
        'Aircraft Model':'机种',
        'UTC Time':'UTC时间',
        'Local Time':'本地时间',
		'Longitude':'经度',
        'Latitude':'纬度',
        'Flight Time':'飞行时间',
        'Remaining Time':'剩余时间',
        'Total Distance':'总里程',
        'Remaining Distance':'剩余里程',
        'Elapsed Distance':'飞行里程',
        'In Flight':'飞行中',
        'Paused':'已暂停',
        'Crashed':'已坠毁',
        'Direction':'方向',
        'AGL':'相对高度',
        'Altitude':'海拔高度',
        'Vertical Speed':'垂直速度',
        'Speed':'速度',
        'Airspeed':'空速',
        'Groundspeed':'地速',
        'Mach':'马赫数',
        'Fuel':'燃料'
    },
	'ja':{
		'Flight Control Center':'飛行制御センター',
		'Loading':'Loading...',
		KEYBOARD_HELP_IDLE:'Esc：終了',
		KEYBOARD_HELP:'Esc：終了    s：ｻｳﾝﾄﾞｵﾝ/ｵﾌ    p：一時停止/再開',
		'No Flight Mission':'飛行任務がありません。',
		'Aircraft Model':'機種',
        'UTC Time':'UTC時間',
        'Local Time':'地方時間',
		'Longitude':'経度',
        'Latitude':'緯度',
        'Flight Time':'飛行時間',
        'Remaining Time':'残り時間',
        'Total Distance':'総距離',
        'Remaining Distance':'残り距離',
        'Elapsed Distance':'飛行距離',
        'In Flight':'飛行中',
        'Paused':'一時停止',
        'Crashed':'墜落しました',
        'Direction':'方向',
        'AGL':'対地高度',
        'Altitude':'海抜高度',
        'Vertical Speed':'垂直速度',
        'Speed':'速度',
        'Airspeed':'対気速度',
        'Groundspeed':'対地速度',
        'Mach':'マッハ数',
        'Fuel':'燃料'
    }
}
module.exports=class{
    data=undefined;
    running=true;
    flightStatus=null;
    constructor(stream,_exit,param={}){
        this._exit=_exit;
        this._timer=null;
        
        this.terminal=new Terminal(stream,{
            outputEncoding:param.encoding
        });
        this.lang=new LanguagePack(LANGUAGE_PACK_DATA,param.language);
        
        this.FGFS_HOST=param.FGFS_HOST;
        this.terminal.clrscr();
        this.terminal.locate(0,0);
        this.terminal.setcursor(false);
        this.terminal.print(this.lang.t('Loading'));
        this.refresh();
    }
    drawFrame(){
        this.terminal.clrscr();
        this.terminal.locate(0,1);
        this.terminal.setattr(Terminal.ATTR_BOLD,Terminal.ATTR_REVERSED,Terminal.FG_YELLOW,Terminal.BG_CYAN);
        this.terminal.print(' '.repeat(79));
        let title=this.lang.t('Flight Control Center');
        this.terminal.locate(Math.round((80-Terminal.strlen(title))/2),1);
        this.terminal.print(title);
        
        this.terminal.locate(0,24);
        this.terminal.setattr(Terminal.RESET_ATTR,Terminal.ATTR_REVERSED,Terminal.FG_BLACK,Terminal.BG_CYAN);
        this.terminal.print(' '.repeat(79));
        this.terminal.locate(2,24);
        this.terminal.print(this.lang.t(this.data ? 'KEYBOARD_HELP' : 'KEYBOARD_HELP_IDLE'),79);
        this.terminal.setattr(Terminal.RESET_ATTR);
    }
    _drawTime(){
        let timestr=fecha.format(new Date(),'YYYY-MM-DD hh:mm:ss');
        this.terminal.setattr(Terminal.ATTR_REVERSED,Terminal.FG_BLACK,Terminal.BG_CYAN);
        this.terminal.locate(80-timestr.length,1);
        this.terminal.print(timestr);
        this.terminal.setattr(Terminal.RESET_ATTR);
    }
    async refresh(){
        if(!this.running){
            return;
        }
        this._timer=setTimeout(()=>{
            if(this.running){
                this.refresh();
            }
        },1000);

        let data=null;
        try{
            data=await axios({
                method:'GET',
                url:this.FGFS_HOST+'/json/fgreport'
            });
            if(!this.running){
                return;
            }
        }catch(e){
            if(!this.running){
                return;
            }
            if(null!==this.data){
                this.data=null;
                this.drawFrame();
                let text=this.lang.t('No Flight Mission');
                this.terminal.locate(Math.floor((80-Terminal.strlen(text))/2),12);
                this.terminal.print(text);
            }
            this._drawTime();
            return;
        }

        try{
            let fgreport={};
            for(let item of data.data.children){
                fgreport[item.name]=item.value;
            }

            this.terminal.setattr(Terminal.RESET_ATTR);

            //绘制框架
            if(!this.data){
                this.data=fgreport;
                this.drawFrame();

                this.terminal.locate(0,3);
                this.terminal.print(this.lang.t('Aircraft Model'));
                this.terminal.locate(0,4);
                this.terminal.print(this.lang.t('UTC Time'));
                this.terminal.locate(0,5);
                this.terminal.print(this.lang.t('Local Time'));
                this.terminal.locate(0,6);
                this.terminal.print(this.lang.t('Longitude'));
                this.terminal.locate(0,7);
                this.terminal.print(this.lang.t('Latitude'));
                this.terminal.locate(0,8);
                this.terminal.print(this.lang.t('Flight Time'));
                this.terminal.locate(0,9);
                this.terminal.print(this.lang.t('Remaining Time'));
                this.terminal.locate(0,10);
                this.terminal.print(this.lang.t('Total Distance'));
                this.terminal.locate(0,11);
                this.terminal.print(this.lang.t('Remaining Distance'));
                this.terminal.locate(0,12);
                this.terminal.print(this.lang.t('Elapsed Distance'));

                this.terminal.locate(40,4);
                this.terminal.print(this.lang.t('Direction'));
                this.terminal.locate(40,5);
                this.terminal.print(this.lang.t('Altitude'));
                this.terminal.locate(40,6);
                this.terminal.print(this.lang.t('AGL'));
                this.terminal.locate(40,7);
                this.terminal.print(this.lang.t('Vertical Speed'));
                if('ufo'==fgreport['flight-model']){
                    this.terminal.locate(40,8);
                    this.terminal.print(this.lang.t('Speed'));
                }else{
                    this.terminal.locate(40,8);
                    this.terminal.print(this.lang.t('Airspeed'));
                    this.terminal.locate(40,9);
                    this.terminal.print(this.lang.t('Groundspeed'));
                    this.terminal.locate(40,10);
                    this.terminal.print(this.lang.t('Mach'));
                    this.terminal.locate(40,11);
                    this.terminal.print(this.lang.t('Fuel'));
                }
            }
            fgreport['longitude'] = Math.abs(fgreport['longitude-deg']).toFixed(6)+(fgreport['longitude-deg']>=0 ? 'E' : 'W');
            fgreport['latitude'] = Math.abs(fgreport['latitude-deg']).toFixed(6)+(fgreport['latitude-deg']>=0 ? 'N' : 'S');
            let padSize=11;
            this.terminal.locate(padSize,3);
            this.terminal.print(fgreport.aircraft+'        ');
            this.terminal.locate(padSize,4);
            this.terminal.print(fgreport['gmt-string']+'        ');
            this.terminal.locate(padSize,5);
            this.terminal.print(fgreport['local-time-string']+'        ');
            this.terminal.locate(padSize,6);
            this.terminal.print(fgreport['longitude']+'        ');
            this.terminal.locate(padSize,7);
            this.terminal.print(fgreport['latitude']+'        ');
            this.terminal.locate(padSize,8);
            this.terminal.print(fgreport['flight-time-string']+'        ');
            this.terminal.locate(padSize,9);
            this.terminal.print(fgreport['ete-string']+'        ');
            this.terminal.locate(padSize,10);
            this.terminal.print(fgreport['total-distance'].toFixed(1)+'nm        ');
            this.terminal.locate(padSize,11);
            this.terminal.print(fgreport['distance-remaining-nm'].toFixed(1)+'nm        ');
            this.terminal.locate(padSize,12);
            this.terminal.print((Number(fgreport['total-distance'])-Number(fgreport['distance-remaining-nm'])).toFixed(1)+'nm        ');
            
            this.terminal.locate(40+padSize,4);
            this.terminal.print((Number(fgreport['heading-deg'])).toFixed(2)+'°        ');
            this.terminal.locate(40+padSize,5);
            this.terminal.print((Number(fgreport['altitude-ft'])).toFixed(1)+'ft        ');
            this.terminal.locate(40+padSize,6);
            this.terminal.print((Number(fgreport['altitude-agl-ft'])).toFixed(1)+'ft        ');
            this.terminal.locate(40+padSize,7);
            this.terminal.print((Number(fgreport['vertical-speed-fps'])*60).toFixed(1)+'ft/min        ');
            if('ufo'==fgreport['flight-model']){
                this.terminal.locate(40+padSize,8);
                this.terminal.print((Number(fgreport['vertical-speed-fps'])).toFixed(1)+'kts        ');
            }else{
                this.terminal.locate(40+padSize,8);
                this.terminal.print((Number(fgreport['airspeed-kt'])).toFixed(1)+'kts        ');
                this.terminal.locate(40+padSize,9);
                this.terminal.print((Number(fgreport['groundspeed-kt'])).toFixed(1)+'kts        ');
                this.terminal.locate(40+padSize,10);
                this.terminal.print((Number(fgreport['mach'])).toFixed(4)+'     ');
                this.terminal.locate(40+padSize,11);
                let fuelPercentage=Number(fgreport['remain-fuel'])/Number(fgreport['initial-fuel'])*100;
                this.terminal.print(fuelPercentage.toFixed(2)+'%     ');
            }

            let status=null;
            if(fgreport['crashed']){
                status='crashed';
            }else if(fgreport['paused']){
                status='paused';
            }else{
                status='running';
            }
            if(this.flightStatus!=status){
                this.flightStatus=status;
                this.terminal.locate(0,23);
                this.terminal.clrline();
                switch(status){
                    case 'crashed':
                        this.terminal.setattr(Terminal.ATTR_BOLD,Terminal.ATTR_UNDERLINE,Terminal.FG_YELLOW,Terminal.BG_RED);
                        this.terminal.print(this.lang.t('Crashed'));
                    break;
                    case 'paused':
                        this.terminal.setattr(Terminal.ATTR_BOLD,Terminal.FG_YELLOW);
                        this.terminal.print(this.lang.t('Paused'));
                    break;
                    default:
                        this.terminal.setattr(Terminal.ATTR_BOLD,Terminal.FG_GREEN);
                        this.terminal.print(this.lang.t('In Flight'));
                    break;
                }
                this.terminal.setattr(Terminal.RESET_ATTR);
                this.terminal.print(' '.repeat(20));
            }
            this._drawTime();
        }catch(e){
            console.error(e);
        }
    }
    destroy(){
        try{
            this.running=false;
            if(this._timer){
              clearTimeout(this._timer);
            }
        }catch(e){
            console.error(e);
        }finally{
            this._exit();
        }
    }
    async toggleSound(){
        let {data}=await axios({
            method:'GET',
            url:this.FGFS_HOST+'/json/sim/sound/enabled'
        });
        await axios({
            method:'GET',
            url:this.FGFS_HOST+`/props/sim/sound?submit=set&enabled=${data.value ? 'false' : 'true'}`
        });
    }
    async togglePause(){
        await axios({
            method:'GET',
            url:this.FGFS_HOST+'/run.cgi?value=pause'
        });
    }
    ondata(data){
        try{
            switch(data[0]){
                case 0x1b:
                    this.terminal.reset();
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
