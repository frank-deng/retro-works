<?php
require('config.php');
abstract class DataManager{
    private $cache_key_data=null;
    private $cache_key_timestamp=null;
    private $timeout=null;
    private $cache_expired=false;
    protected $data=null;
    protected $ch=null;
    protected function __construct($cache_key,$timeout=null){
        global $_CONFIG;
        $this->cache_key_data=$cache_key.'_data';
        $this->cache_key_timestamp=$cache_key.'_timeout';
        $this->timeout=$timeout;

        //Load data from cache
        $data=apcu_fetch($this->cache_key_data);
        if(!$data){
            $this->cache_expired=true;
        }else{
            $this->data=$data;
            //Check if cache expired
            $timestamp=apcu_fetch($this->cache_key_timestamp);
            if($this->timeout && (!$timestamp || ((time()-$timestamp) > $this->timeout))){
                $this->cache_expired=true;
            }
        }
    }
    protected function cacheExpired(){
        return $this->cache_expired;
    }
    protected function writeCache($data){
        apcu_add($this->cache_key_data,null);
        apcu_store($this->cache_key_data,$data);
        apcu_add($this->cache_key_timestamp,null);
        apcu_store($this->cache_key_timestamp,time());
    }
    public function getHandle(){
        return $this->ch;
    }
    public function onFinish(){
        $this->data=curl_multi_getcontent($this->ch);
    }
    public function fetch(){
        return $this->data;
    }
}
function fetchMultiWait(...$arr){
    $taskList=[];
    foreach($arr as $object){
        if(!($object instanceof DataManager)){
            continue;
        }
        $handle=$object->getHandle();
        if(!$handle){
            continue;
        }
        array_push($taskList,$object);
    }
    if(!count($taskList)){
        return;
    }

    $task=curl_multi_init();
    try{
        foreach($taskList as $object){
            $handle=$object->getHandle();
            if(!is_array($handle)){
                curl_multi_add_handle($task,$handle);
                continue;
            }
            foreach($handle as $subHandle){
                curl_multi_add_handle($task,$subHandle);
            }
        }
        $status=$active=null;
        do{
            $status=curl_multi_exec($task,$active);
            if($active){
                curl_multi_select($task);
            }
        }while($active && CURLM_OK==$status);
        foreach($taskList as $object){
            $object->onFinish();
        }
    }catch(Exception $e){
        error_log($e);
    }finally{
        foreach($taskList as $object){
            $handle=$object->getHandle();
            if(!is_array($handle)){
                curl_multi_remove_handle($task,$handle);
                continue;
            }
            foreach($handle as $subHandle){
                curl_multi_remove_handle($task,$subHandle);
            }
        }
    }
}

class FetchNews extends DataManager{
    public function __construct(){
        global $_CONFIG;
        parent::__construct('news', 60*3);
        if($this->cacheExpired()){
            $ch=curl_init();
            curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
            curl_setopt($ch, CURLOPT_TIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
            curl_setopt($ch, CURLOPT_POST, 1);
            curl_setopt($ch, CURLOPT_ENCODING, 'UTF-8');
            curl_setopt($ch, CURLOPT_URL, 'http://api.tianapi.com/bulletin/index');
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
            curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query(array(
              'key'=>$_CONFIG['TIANAPI_KEY']
            )));
            $this->ch=$ch;
        }
    }
    public function onFinish(){
        try{
            $data=curl_multi_getcontent($this->ch);
            if($data){
                $this->data=json_decode($data,true)['newslist'];
                $this->writeCache($this->data);
            }
        }catch(Exception $e){
            error_log($e);
        }
    }
}
class FetchNcov extends DataManager{
    public function __construct(){
        global $_CONFIG;
        parent::__construct('ncov', 60*10);
        if($this->cacheExpired()){
            $ch=curl_init();
            curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
            curl_setopt($ch, CURLOPT_TIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
            curl_setopt($ch, CURLOPT_POST, 1);
            curl_setopt($ch, CURLOPT_ENCODING, 'UTF-8');
            curl_setopt($ch, CURLOPT_URL, 'http://api.tianapi.com/txapi/ncov/index');
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
            curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query(array(
              'key'=>$_CONFIG['TIANAPI_KEY']
            )));
            $this->ch=$ch;
        }
    }
    public function onFinish(){
        try{
            $data=curl_multi_getcontent($this->ch);
            if($data){
                $this->data=json_decode($data,true)['newslist'][0];
                $this->writeCache($this->data);
            }
        }catch(Exception $e){
            error_log($e);
        }
    }
}
class FetchWeather extends DataManager{
    private $location_id=null;
    private $location_name=null;
    private static $urlList=[
        [
            'type'=>'now',
            'url'=>'https://devapi.qweather.com/v7/weather/now',
            'key'=>'now',
        ],
        [
            'type'=>'air',
            'url'=>'https://devapi.qweather.com/v7/air/now',
            'key'=>'now',
        ],
        [
            'type'=>'forecast',
            'url'=>'https://devapi.qweather.com/v7/weather/3d',
            'key'=>'daily',
        ],
        [
            'type'=>'warning',
            'url'=>'https://devapi.qweather.com/v7/warning/now',
            'key'=>'warning',
        ],
        [
            'type'=>'indices',
            'url'=>'https://devapi.qweather.com/v7/indices/1d',
            'key'=>'daily',
            'query'=>['type'=>0]
        ]
    ];
    public static function clearCache(){
        apcu_delete('weather_data');
    }
    public function __construct($location_id=null, $location_name=null){
        global $_CONFIG;
        parent::__construct('weather',10);
        $this->location_id=$location_id;
        $this->location_name=$location_name;
        if(!$this->cacheExpired()){
            return;
        }

        $this->ch=[];
        foreach(self::$urlList as $url){
            $ch=curl_init();
            $query=[
                'location'=>$this->location_id,
                'key'=>$_CONFIG['HEWEATHER_KEY']
            ];
            if(isset($url['query'])){
                $query=array_merge($url['query'],$query);
            }
            curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
            curl_setopt($ch, CURLOPT_TIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
            curl_setopt($ch, CURLOPT_POST, 0);
            curl_setopt($ch, CURLOPT_ENCODING, 'UTF-8');
            curl_setopt($ch, CURLOPT_URL, $url['url'].'?'.http_build_query($query));
            curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, FALSE);
            curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, FALSE);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
            array_push($this->ch,$ch);
        }
    }
    public function onFinish(){
        try{
            $data=$this->fetch();
            if(!$data){
                $data=[];
            }
            foreach($this->ch as $i=>$ch){
                $url=self::$urlList[$i];
                switch($url['type']){
                    case 'warning':
                        $data['warning']=null;
                    break;
                }
                $newData=curl_multi_getcontent($ch);
                if(!$newData){
                    continue;
                }
                $newData=json_decode($newData,true);
                if(200!=$newData['code']){
                    error_log('Load data failed: '.$url['url']);
                    continue;
                }
                $data[$url['type']]=$newData[$url['key']];
            }
            $this->data=$data;
            $this->writeCache($this->data);
        }catch(Exception $e){
            error_log($e);
        }
    }
    public function getLocationName($simple=false){
        if(!$simple){
            return $this->location_name;
        }
        return end(explode('-',$this->location_name));
    }
}

