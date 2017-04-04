<?php
if (!defined('IN_SITE')) {
	exit('Access Denied!');
}

//Load external libraries
require_once('source/Parsedown.php');
require_once('source/api.php');

//Utils
function lang($string, $input = false, $language = false){
	global $_G;
	if (!$language || !isset($_G['lang'][$language])) {
		$language = $_G['config']['language'];
	}
	if (isset($_G['lang'][$language][$string])) {
		$string = $_G['lang'][$language][$string];
		if (false !== $input) {
			foreach ($input as $k => $v) {
				$string = preg_replace('/\{'.preg_quote($k, '/').'\}/', $v, $string);
			}
		}
	}
	return $string;
}
function pager($base_url, $pagevar, $totalpage, $curpage) {
	$pagevar = htmlspecialchars($pagevar);
	$totalpage = intval($totalpage);
	$curpage = intval($curpage);
	$base_url_parsed = parse_url($base_url);
	$path = $base_url_parsed['path'];
	parse_str($base_url_parsed['query'], $query);
	$query_prev = $query_next = $query;
	$query_prev[$pagevar] = $curpage - 1;
	$query_next[$pagevar] = $curpage + 1;
	
	$result = "<form action=\"{$path}\" method='GET'>";
	if ($curpage > 1) {
		$result .= "<a href=\"".$path.'?'.http_build_query($query_prev)."\">&lt;".lang('Prev Page')."</a>&nbsp;";
	}
	if ($curpage < $totalpage) {
		$result .= "<a href=\"".$path.'?'.http_build_query($query_next)."\">".lang('Next Page')."&gt;</a>&nbsp;";
	}
	$result .= lang('_jump_page', array(
		'total' => $totalpage,
		'input' => "<input type='text' name='page' maxlength='".strlen((string)$totalpage)."' size='".strlen((string)$totalpage)."' value='{$curpage}'/>",
	));
	$result .= "&nbsp;<input type='submit' value='".lang('OK')."'/>";
	foreach($query as $k => $v) {
		if ($k != $pagevar) {
			$result .= "<input type='hidden' name='".htmlspecialchars($k)."' value='".htmlspecialchars($v)."'/>";
		}
	}
	$result .= '</form>';
	return $result;
}
function showAPIMakeRequest($url, $params, $post = false) {
	global $_G;
	$result = array('url' => $url);
	$params['showapi_appid'] = $_G['config']['showAPI']['appid'];

	//Get value of showapi_sign
	ksort($params);
	$signStr = '';
	foreach($params as $k => $v) {
		$signStr .= $k.$v;
	}
	$signStr .= $_G['config']['showAPI']['secret'];
	$params['showapi_sign'] = strtolower(md5($signStr));

	if ($post) {
		$result['post'] = $params;
	} else {
		$result['url'] .= '?'.http_build_query($params);
	}
	return $result;
}
function fetchJSON($requests_all, $multi = false) {
	global $_G;
	if ($multi){
		$handlesAll = array();
		$result = array();

		//Prepare connections
		$mh = curl_multi_init();
		foreach ($requests_all as $key => $request) {
			$handlesAll[$key] = curl_init($request['url']);

			$curl_config = array(
				CURLOPT_RETURNTRANSFER => 1,
				CURLOPT_TIMEOUT => $_G['config']['curlTimeout'],
				CURLOPT_FOLLOWLOCATION => 1,
			);
			if (isset($request['post'])) {
				$curl_config[CURLOPT_POST] = 1;
				$curl_config[CURLOPT_POSTFIELDS] = $request['post'];
			}
			if (isset($request['headers']) && 'array' == gettype($request['headers'])) {
				$curl_config[CURLOPT_HTTPHEADER] = $request['headers'];
			}
			curl_setopt_array($handlesAll[$key], $curl_config);
			curl_multi_add_handle($mh, $handlesAll[$key]);
		}

		//Do fetch data
		$running = null;
		do {
			curl_multi_exec($mh, $running);
			usleep(100000);
		} while ($running);

		//Process data and Close Connections for each curl handle
		foreach ($handlesAll as $key => $ch) {
			$res = curl_multi_getcontent($ch);
			$result[$key] = ($res ? json_decode($res, true) : false);
			curl_multi_remove_handle($mh, $ch);
		}
		curl_multi_close($mh);

		return $result;
	} else {
		$request = $requests_all;
		$ch = curl_init($request['url']);

		$curl_config = array(
			CURLOPT_RETURNTRANSFER => 1,
			CURLOPT_TIMEOUT => $_G['config']['curlTimeout'],
			CURLOPT_FOLLOWLOCATION => 1,
		);
		if (isset($request['post'])) {
			$curl_config[CURLOPT_POST] = 1;
			$curl_config[CURLOPT_POSTFIELDS] = $request['post'];
		}
		if (isset($request['headers']) && 'array' == gettype($request['headers'])) {
			$curl_config[CURLOPT_HTTPHEADER] = $request['headers'];
		}
		curl_setopt_array($ch, $curl_config);
		$res = curl_exec($ch);
		curl_close($ch);
		return ($res ? json_decode($res, true) : false);;
	}
}
class Cache {
	private $data = Array();
	private $changed = false;
	private $clear = false;
	private $db;
	private static $instance;
	public function __construct($conn, $user, $password){
		$this->db = new PDO($conn, $user, $password);
		$stmt = $this->db->prepare('SELECT ckey,cdata from cache_table where ckey=\'cache\'');
		$stmt->execute();
		$result = $stmt->fetchAll(PDO::FETCH_ASSOC);
		if (count($result) > 0 && $result[0]['cdata']) {
			$this->data = unserialize($result[0]['cdata']);
		} else {
			$stmt = $this->db->prepare('INSERT INTO cache_table (ckey, cdata) VALUES (\'cache\', \'\')');
			$stmt->execute();
		}
		static::$instance = $this;
	}
	public function __destruct(){
		if ($this->clear) {
			$stmt = $this->db->prepare('UPDATE cache_table SET cdata = null where ckey = \'cache\'');
			$stmt->execute();
		} else if ($this->changed) {
			$stmt = $this->db->prepare('UPDATE cache_table SET cdata = :value where ckey = \'cache\'');
			$stmt->bindValue('value', serialize($this->data));
			$stmt->execute();
		}
	}
	public static function Instance(){
		return static::$instance;
	}
	public function get($key) {
		if (!isset($this->data[$key])) {
			return false;
		}
		return $this->data[$key];
	}
	public function set($key, $value) {
		$this->changed = true;
		$this->clear = false;
		$this->data[$key] = $value;
	}
	public function delete($key) {
		$this->changed = true;
		if (isset($this->data[$key])) {
			unset($this->data[$key]);
			return true;
		} else {
			return false;
		}
	}
	public function clear() {
		$this->clear = true;
		$this->data = Array();
	}
}

//Setup global variable
$_G = array();

//Load config
$_G['config'] = require('config.php'); 

//Set timezone
date_default_timezone_set($_G['config']['timezone']);

//Load language packs
$_G['lang']['zh-CN'] = require('source/lang_zh-CN.php');

//Load Cache
new Cache($_G['config']['dbcache']['conn'], $_G['config']['dbcache']['user'], $_G['config']['dbcache']['password']);

