<?php
if (!defined('IN_SITE')) {
	exit('Access Denied!');
}
function getArticles(){
	global $_G;
	$data = Cache::Instance()->get('mySpaceArticles');
	if (!isset($data['timestamp'])
		|| $data['timestamp'] != filemtime($_G['config']['articlePath'].DIRECTORY_SEPARATOR.'.')
		|| time() - $data['timestamp'] > $_G['config']['articleCacheTimeout']) {
		//Get article files
		$files = [];
		foreach (scandir($_G['config']['articlePath']) as $filename) {
			$filename = realpath($_G['config']['articlePath'].DIRECTORY_SEPARATOR.$filename);
			if (is_file($filename) && preg_match('/\.md$/', $filename) && strpos(mime_content_type($filename), 'text') !== false) {
				$files[] = $filename;
			}
		}
	
		//Get title of articles
		$data = array(
			'content' => array(),
			'timestamp' => filemtime($_G['config']['articlePath'].DIRECTORY_SEPARATOR.'.'),
		);
		foreach($files as $i => $article_file) {
			$article = file($article_file);
			if ($article) {
				$data['content'][] = array(
					'id' => md5(basename($article_file, '.md')),
					'title' => htmlspecialchars(mb_substr(trim(preg_replace('/^#+\s*/', '', $article[0])), 0, 30)),
					'file' => $article_file,
					'mtime' => filemtime($article_file),
				);
			}
		}
		usort($data['content'], function($a, $b){
			if ($a['mtime'] == $b['mtime']) {
				return strcmp($a['title'], $b['title']);
			} else {
				return $a['mtime'] < $b['mtime'] ? 1 : -1;
			}
		});
		Cache::Instance()->set('mySpaceArticles', $data);
	}
	return $data['content'];
}
function getArticleDetail($id){
	foreach (getArticles() as $article) {
		if ($article['id'] == strtolower($id)) {
			$markdown = file_get_contents($article['file']);
			if (!$markdown) {
				return false;
			} else {
				$parser = new Parsedown();
				return ['title' => $article['title'], 'content' => $parser->text($markdown)];
			}
		}
	}
	return false;
}
function getJokes($page = 1){
	$data = fetchJSON(showAPIMakeRequest('http://route.showapi.com/341-1', array('page'=>$page, 'maxResult'=>19)));
	if (isset($data['showapi_res_code']) && $data['showapi_res_code'] == 0) {
		processJokes($data['showapi_res_body']);
		return $data['showapi_res_body'];
	} else {
		return false;
	}
}
function processJokes(&$data){
	global $_G;
	try{
		$db = new PDO($_G['config']['dbcache']['conn'], $_G['config']['dbcache']['user'], $_G['config']['dbcache']['password']);
		foreach($data['contentlist'] as $idx => $content) {
			$stmt_i = $db->prepare('REPLACE INTO showapi_jokes (ckey, cdata) VALUES (:key, :content)');
			$stmt_i->bindValue('key', $content['id']);
			$stmt_i->bindValue('content', serialize(array(
				'id' => $content['id'],
				'title' => $content['title'],
				'text' => $content['text'],
				'ct' => $content['ct'],
			)));
			$stmt_i->execute();
		}
	}catch(Exception $e){}
}
function getJokeDetail($key) {
	global $_G;
	$result = false;
	try{
		$db = new PDO($_G['config']['dbcache']['conn'], $_G['config']['dbcache']['user'], $_G['config']['dbcache']['password']);
		$stmt_s = $db->prepare('SELECT cdata from showapi_jokes WHERE ckey = :key');
		$stmt_s->bindValue('key', $key);
		$res = $stmt_s->execute();
		$result = unserialize($stmt_s->fetchAll(PDO::FETCH_ASSOC)[0]['cdata']);
	}catch(Exception $e){}
	return $result;
}
function newsGetChannels($refresh = false) {
	global $_G;
	$data = Cache::Instance()->get('channelList');
	if ($data && !$refresh) {
		return $data;
	}

	$data = fetchJSON(showAPIMakeRequest('http://route.showapi.com/109-34'));
	if (isset($data['showapi_res_code']) && $data['showapi_res_code'] == 0) {
		$result = Array('0' => lang('Up To Date'));
		foreach($data['showapi_res_body']['channelList'] as $record) {
			$result[$record['channelId']] = $record['name'];
		}
		Cache::Instance()->set('channelList', $result);
		return $result;
	} else {
		return false;
	}
}
function newsGetChannelName($channelId = false) {
	global $_G;
	if (!$channelId || !preg_match('/^[A-Za-z0-9]+$/', $channelId)) {
		return lang('Up To Date');
	}
	$channels = newsGetChannels();
	if (!$channels || !isset($channels[$channelId])) {
		return lang('Up To Date');
	} else {
		return $channels[$channelId];
	}
}
function newsGetList($channel = false, $page = 1, $keyword = false) {
	$params = Array(
		'page' => $page,
		'needHtml' => 0,
		'needContent' => 0,
		'needAllList' => 1,
		'maxResult' => 19,
	);
	if ($channel && preg_match('/^[A-Za-z0-9]+$/', $channel)) {
		$params['channelId'] = $channel;
	}
	if ($keyword) {
		$params['title'] = $keyword;
	}
	$data = fetchJSON(showAPIMakeRequest('http://route.showapi.com/109-35', $params));
	if (isset($data['showapi_res_code']) && $data['showapi_res_code'] == 0) {
		newsProcessList($data['showapi_res_body']['pagebean']);
		return $data['showapi_res_body']['pagebean'];
	} else {
		return false;
	}
}
function newsProcessList(&$data){
	global $_G;
	$db = new PDO($_G['config']['dbcache']['conn'], $_G['config']['dbcache']['user'], $_G['config']['dbcache']['password']);
	$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
	$db->setAttribute(PDO::ATTR_EMULATE_PREPARES, false);
	try{
		foreach($data['contentlist'] as $idx => $content) {
			if (!$content['title'] || $content['title'] == '') {
				foreach ($content['allList'] as $titleCandidate) {
					if ('string' == gettype($titleCandidate)) {
						$content['title'] = $data['contentlist'][$idx]['title'] = preg_replace('/^(\s|　)+/', '', mb_substr($titleCandidate, 0, 25, 'utf-8'));
						break;
					}
				}
			}
			$content['html'] = '';
			foreach ($content['allList'] as $line){
				if (is_string($line)) {
					$content['html'] .= '<p>'.htmlspecialchars($line).'</p>';
				}
			}
			$content['key'] = $data['contentlist'][$idx]['key'] = md5($content['title'].$content['source'].$content['pubDate'].$content['html']);

			//Check if record exists
			$stmt_i = $db->prepare('REPLACE INTO showapi_news (ckey, cdata) VALUES (:key, :content)');
			$stmt_i->bindValue('key', $data['contentlist'][$idx]['key'], PDO::PARAM_STR);
			$stmt_i->bindValue('content', serialize(array(
				'key' => $content['key'],
				'title' => $content['title'],
				'source' => $content['source'],
				'pubDate' => $content['pubDate'],
				'html' => $content['html'],
			)), PDO::PARAM_STR);
			$stmt_i->execute();
		}
	}catch(Exception $e){}
}
function newsGetDetail($key) {
	global $_G;
	$result = false;
	try{
		$db = new PDO($_G['config']['dbcache']['conn'], $_G['config']['dbcache']['user'], $_G['config']['dbcache']['password']);
		$stmt_s = $db->prepare('SELECT cdata from showapi_news WHERE ckey = :key');
		$stmt_s->bindValue('key', $key);
		$stmt_s->execute();
		$result = unserialize($stmt_s->fetchAll(PDO::FETCH_ASSOC)[0]['cdata']);
	}catch(Exception $e){}
	return $result;
}
function getWeatherInfo($city) {
	global $_G;
	if (!$city) {
		return false;
	}
	$weather_data = fetchJSON(array(
		'url' => 'https://free-api.heweather.com/v5/weather',
		'post' => http_build_query(array(
			'city' => $city,
			'key' => $_G['config']['heweather_key'],
		)),
	));
	if (!$weather_data) {
		return false;
	}
	$weather = $weather_data['HeWeather5'][0];
	if ($weather['status'] == 'ok') {
		return $weather;
	} else {
		return false;
	}
}
function processMovieRank($daily, $weekly, $weekend){
	$result = array();
	if ($daily && isset($daily['showapi_res_body']['ret_code']) && $daily['showapi_res_body']['ret_code'] == 0) {
		$result['daily'] = $daily['showapi_res_body']['datalist'];
		usort($result['daily'], function($a, $b){
			return $a['Rank'] > $b['Rank'];
		});
	} else {
		return false;
	}
	if ($weekly && isset($weekly['showapi_res_body']['ret_code']) && $weekly['showapi_res_body']['ret_code'] == 0) {
		$result['weekly'] = $weekly['showapi_res_body']['datalist'];
		usort($result['weekly'], function($a, $b){
			return $a['Rank'] > $b['Rank'];
		});
	} else {
		return false;
	}
	if ($weekend && isset($weekend['showapi_res_body']['ret_code']) && $weekend['showapi_res_body']['ret_code'] == 0) {
		$result['weekend'] = $weekend['showapi_res_body']['datalist'];
		usort($result['weekend'], function($a, $b){
			return $a['MovieRank'] > $b['MovieRank'];
		});
	} else {
		return false;
	}
	return $result;
}
function getIndexPageData($city) {
	global $_G;
	$result = array('weather' => false, 'news' => false, 'jokes' => false, 'movieRank' => false);

	//Fetch data
	$requestArr = array(
		'news' => showAPIMakeRequest('http://route.showapi.com/109-35', Array(
			'page' => 1,
			'needHtml' => 0,
			'needContent' => 0,
			'needAllList' => 1,
			'maxResult' => 10,
			'showapi_timestamp' => date('YmdHis'),
		)),
		'jokes' => showAPIMakeRequest('http://route.showapi.com/341-1', Array(
			'page' => 1,
			'maxResult' => 10,
			'showapi_timestamp' => date('YmdHis'),
		)),
		'movieRankWeekly' => showAPIMakeRequest('http://route.showapi.com/578-1'),
		'movieRankDaily' => showAPIMakeRequest('http://route.showapi.com/578-2'),
		'movieRankWeekend' => showAPIMakeRequest('http://route.showapi.com/578-3'),
	);
	if ($city) {
		$requestArr['weather'] = array(
			'url' => 'https://free-api.heweather.com/v5/weather',
			'post' => http_build_query(array(
				'city' => $city,
				'key' => $_G['config']['heweather_key'],
			)),
		);
	}

	$jsonArr = fetchJSON($requestArr, true);
	if (isset($jsonArr['news']['showapi_res_code']) && $jsonArr['news']['showapi_res_code'] == 0) {
		newsProcessList($jsonArr['news']['showapi_res_body']['pagebean']);
		$result['news'] = $jsonArr['news']['showapi_res_body']['pagebean'];
	}
	if (isset($jsonArr['jokes']['showapi_res_code']) && $jsonArr['jokes']['showapi_res_code'] == 0) {
		processJokes($jsonArr['jokes']['showapi_res_body']);
		$result['jokes'] = $jsonArr['jokes']['showapi_res_body'];
	}
	if ($city && $jsonArr['weather']['HeWeather5'][0]['status'] == 'ok') {
		$result['weather'] = $jsonArr['weather']['HeWeather5'][0];
	}
	$movieRank = processMovieRank($jsonArr['movieRankDaily'], $jsonArr['movieRankWeekly'], $jsonArr['movieRankWeekend']);
	if ($movieRank) {
		$result['movieRank'] = $movieRank;
	}

	return $result;
}
function getPhoneNumInfo($phone) {
	global $_G;
	$res_data = fetchJSON(showAPIMakeRequest('https://route.showapi.com/6-1', array('num' => $phone)));
	if ($res_data && $res_data['showapi_res_code'] == 0) {
		return $res_data['showapi_res_body'];
	} else {
		return false;
	}
}
function getCurrencies() {
	global $_G;
	$res_data = fetchJSON(showAPIMakeRequest('http://route.showapi.com/105-30'));
	if ($res_data && $res_data['showapi_res_code'] == 0 && $res_data['showapi_res_body']['ret_code'] == 0) {
		usort($res_data['showapi_res_body']['list'], function($a, $b){
			return strcmp($a['code'], $b['code']);
		});
		return $res_data['showapi_res_body']['list'];
	} else {
		return false;
	}
}
function doCurrencyExchange($from, $to, $amount) {
	global $_G;
	$res_data = fetchJSON(showAPIMakeRequest('http://route.showapi.com/105-31', array(
		'fromCode' => $from,
		'toCode' => $to,
		'money' => $amount,
	)));
	if ($res_data && $res_data['showapi_res_code'] == 0 && $res_data['showapi_res_body']['ret_code'] == 0) {
		return $res_data['showapi_res_body']['money'];
	} else {
		return false;
	}
}
function queryDictionary($word, $srclang = false, $destlang = false) {
	global $_G;
	$ch = curl_init('http://fy.webxml.com.cn/webservices/EnglishChinese.asmx/Translator');
	curl_setopt_array($ch, array(
		CURLOPT_RETURNTRANSFER => 1,
		CURLOPT_TIMEOUT => $_G['config']['curlTimeout'],
		CURLOPT_FOLLOWLOCATION => 1,
		CURLOPT_POST => 1,
		CURLOPT_POSTFIELDS => 'wordKey='.str_replace(array("\r", "\n"), array('', ''), $word),
	));
	$res = curl_exec($ch);
	curl_close($ch);
	if (!$res) {
		return false;
	}

	try {
		$xml = new SimpleXMLElement($res);
		$xml->registerXPathNamespace('diffgr', 'urn:schemas-microsoft-com:xml-diffgram-v1');
		return $xml->xpath('//diffgr:diffgram/Dictionary');
	} catch (Exception $e) {
		return false;
	}
}
function sendMessage($sendto, $message) {
	global $_G;
	if (!isset($_G['config']['messageTarget'][$sendto])) {
		return false;
	}
	$ch = curl_init($_G['config']['messageTarget'][$sendto]);
	curl_setopt_array($ch, array(
		CURLOPT_RETURNTRANSFER => 1,
		CURLOPT_TIMEOUT => $_G['config']['curlTimeout'],
		CURLOPT_FOLLOWLOCATION => 1,
		CURLOPT_POST => 1,
		CURLOPT_POSTFIELDS => http_build_query(array('message' => $message)),
	));
	curl_exec($ch);
	$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
	curl_close($ch);
	return (200 == $httpCode);
}

