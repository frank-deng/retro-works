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
        $this->cache_expired=true;
    }
    protected function cacheExpired(){
        return $this->cache_expired;
    }
    protected function writeCache($data){
    }
    public function getHandle(){
        return $this->ch;
    }
    public function onFinish(){
        if ($this->ch) {
            $this->data=curl_multi_getcontent($this->ch);
        }
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
            if (!$handle) {
                continue;
            }
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
            if (!$handle) {
                continue;
            }
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
    private $enabled=true;
    public function __construct($enabled=true){
        global $_CONFIG;
        parent::__construct('news', 60*3);
        $this->enabled=$enabled;
        if($this->enabled && $this->cacheExpired()){
            $ch=curl_init();
            curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
            curl_setopt($ch, CURLOPT_TIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
            curl_setopt($ch, CURLOPT_POST, 1);
            curl_setopt($ch, CURLOPT_ENCODING, 'UTF-8');
            curl_setopt($ch, CURLOPT_URL, 'https://apis.tianapi.com/guonei/index');
            curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, FALSE);
            curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, FALSE);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
            curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query(array(
              'key'=>$_CONFIG['TIANAPI_KEY'],
              'num'=>50
            )));
            $this->ch=$ch;
        }
    }
    public function onFinish(){
        try{
            if(!$this->enabled){
                $this->data=null;
                return;
            }
            $data=curl_multi_getcontent($this->ch);
            if($data){
                $this->data=json_decode($data,true)['result']['newslist'];
                foreach($this->data as $idx=>$item){
                    $this->data[$idx]['detail_key']=base64_encode($item['url']);
                }
                $this->writeCache($this->data);
            }
        }catch(Exception $e){
            error_log($e);
        }
    }
}
class FetchNewsDetail extends DataManager{
    public function __construct($url){
        global $_CONFIG;
        parent::__construct('news_detail', 60*3);
        if($this->cacheExpired()){
            $ch=curl_init();
            curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
            curl_setopt($ch, CURLOPT_TIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
            curl_setopt($ch, CURLOPT_POST, 1);
            curl_setopt($ch, CURLOPT_ENCODING, 'UTF-8');
            curl_setopt($ch, CURLOPT_URL, 'https://apis.tianapi.com/htmltext/index');
            curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, FALSE);
            curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, FALSE);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
            curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query(array(
              'key'=>$_CONFIG['TIANAPI_KEY'],
              'url'=>$url
            )));
            $this->ch=$ch;
        }
    }
    public function onFinish(){
        try{
            $data=curl_multi_getcontent($this->ch);
            if($data){
                $this->data=json_decode($data,true)['result'];
                $this->writeCache($this->data);
            }
        }catch(Exception $e){
            error_log($e);
        }
    }
}
class FetchImage extends DataManager{
    public function __construct($url){
        global $_CONFIG;
        parent::__construct('news_detail', 60*3);
        if($this->cacheExpired()){
            $ch=curl_init();
            curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
            curl_setopt($ch, CURLOPT_TIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
            curl_setopt($ch, CURLOPT_POST, 0);
            curl_setopt($ch, CURLOPT_ENCODING, 'UTF-8');
            curl_setopt($ch, CURLOPT_URL, $url);
            curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, FALSE);
            curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, FALSE);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
            $this->ch=$ch;
        }
    }
    public function onFinish(){
        try{
            $data=curl_multi_getcontent($this->ch);
            if($data){
                $this->data=$data;
                $this->writeCache($this->data);
            }
        }catch(Exception $e){
            error_log($e);
        }
    }
}
class FetchBlogs extends DataManager{
    public function __construct(){
        global $_CONFIG;
        try{
            parent::__construct('blogs', 60*10);
            if (!$_CONFIG['BLOGS_DATA']) {
                return;
            }
	    if (!file_exists($_CONFIG['BLOGS_DATA'])){
		return;
	    }
            $blogsData = file_get_contents($_CONFIG['BLOGS_DATA']);
            if (!$blogsData) {
                return;
            }
            $this->data = array_slice(json_decode($blogsData, true), 0, $_CONFIG['BLOGS_COUNT']);
            $this->writeCache($this->data);
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
function GetAccessToken($id, $secret){
    global $_CONFIG;
    $ch=curl_init();
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
    curl_setopt($ch, CURLOPT_TIMEOUT, $_CONFIG['REQUEST_TIMEOUT']);
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_URL, 'https://aip.baidubce.com/oauth/2.0/token');
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, FALSE);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, FALSE);
    curl_setopt($ch, CURLOPT_ENCODING, 'UTF-8');
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query(array(
        'grant_type' => 'client_credentials',
        'client_id' => $id,
        'client_secret' => $secret
    )));
    $resp=curl_exec($ch);
    curl_close($ch);
    $token_data=json_decode($resp,true);
    if(!$token_data || !$token_data['access_token']){
        return null;
    }
    return $token_data['access_token'];
}
