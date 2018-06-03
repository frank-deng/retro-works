LANGDATA = {};
LANGDATA['zh-CN'] = {
    '_title_spacer': '&gt;'+'&nbsp;'*80,
    'About' : 'Powered by: 易源接口&nbsp;和风全球天气',
    '_sep' : '｜',
    '_point' : '·',
    
    'Index' : '首页',
    'OK' : '确定',
    'Back' : '返回',
    'Query' : '查询',
    'Query Failed' : '查询失败',
    'Back Home Page' : '回首页',
    'Reload' : '重新加载',
    'Error' : '出错了',
    'Date' : '日期',

    'Centidegree' : '℃',
    'Weather Forecast' : '天气预报',
    'Weather Detail' : '天气详情',
    'Failed To Fetch Weather' : '获取天气预报失败',
    'No Weather Information' : '没有天气信息',
    'Change City' : '更换城市',
    'More Forecast' : '明后天天气预报',
    'Weather' : '天气',
    'Temperature' : '温度',
    'Humidity' : '湿度',
    'UVLevel' : '紫外线指数',
    'Visibility' : '能见度',
    'Wind Direction' : '风向',
    'Wind Speed' : '风速',
    'AQI' : 'AQI：',
    'AQI2' : '空气污染指数',
    'AQILevel' : '空气质量等级',
    'Weather Suggestion' : '气象指数',
    '_suggestion' : {
        'air' : '空气污染指数：',
        'comf' : '人体舒适指数：',
        'cw' : '洗车指数：',
        'drsg' : '穿衣指数：',
        'flu' : '感冒指数：',
        'sport' : '运动指数：',
        'trav' : '旅行指数：',
        'uv' : '紫外线指数：',
    },

    '_date_format' : '%Y年%m月%d日',
    '_week_format' : ['星期一','星期二','星期三','星期四','星期五','星期六','星期日'],

    'More' : '更多',
    'Prev Page' : '上一页',
    'Next Page' : '下一页',
    '_jump_page' : '第%d页&nbsp;共%d页&nbsp;到第%s页',

    'Search' : '搜索',

    'News': '最新资讯',
    'No News' : '获取新闻失败',
    
    'Currency Exchange' : '汇率换算',
    'Exchange' : '兑换',
    'Select Currency' : '选择币种',
    'Initialization Failed' : '初始化失败',
    'Realtime Exchange Rate' : '实时汇率',
    'Currency Code' : '货币代码',
    'Currency Name' : '货币名称',
    'hui_in' : '现汇买入价',
    'chao_in' : '现钞买入价',
    'hui_out' : '现汇卖出价',
    'chao_out' : '现钞卖出价',
    'zhesuan' : '中行折算价',

    'Dictionary' : '英汉词典',
    '_about_dict' : 'Powered By: http://www.webxml.com.cn/',
    'Query Dictionary' : '查词典',
    'Meaning' : '释义',
    'Not Found' : '未找到释义',
    'Sentence Example' : '例句',
    'See Also' : '参见',

    'Failed to load article' : '文章加载失败',
    'Articles' : '文章列表',
    'More Articles': '更多文章',
};

import config;
def lang(index):
    global LANGDATA;
    try:
        return LANGDATA[config.LANGUAGE][index];
    except KeyError:
        return index;

