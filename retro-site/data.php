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
            curl_multi_add_handle($task,$object->getHandle());
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
            curl_multi_remove_handle($task,$object->getHandle());
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
    public function __construct(){
        global $_CONFIG;
        parent::__construct('weather');
        $ch=curl_init();
        curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
        curl_setopt($ch, CURLOPT_TIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
        curl_setopt($ch, CURLOPT_POST, 1);
        curl_setopt($ch, CURLOPT_URL, 'https://free-api.heweather.com/v5/weather');
        curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, FALSE);
        curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, FALSE);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query(array(
            'city'=>$_CONFIG['HEWEATHER_CITY'],
            'key'=>$_CONFIG['HEWEATHER_KEY']
        )));
        $this->ch=$ch;
    }
    public function onFinish(){
        try{
            $data=curl_multi_getcontent($this->ch);
            if($data){
                $this->data=json_decode($data,true)['HeWeather5'][0];
                $this->writeCache($this->data);
            }
        }catch(Exception $e){
            error_log($e);
        }
    }
}

