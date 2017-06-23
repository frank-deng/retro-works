set names utf8;
CREATE DATABASE IF NOT EXISTS telnet_site DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
use telnet_site;
create user telnetsite;
grant insert,delete,update,select on telnet_site.* to telnetsite;
set password for telnetsite=password('telnet-site');
create table if not exists showapi_news(
	ckey varchar(33) not null,
	cdata longtext,
	PRIMARY KEY (ckey)
) DEFAULT CHARSET=utf8;
create table if not exists showapi_jokes(
	ckey varchar(33) not null,
	cdata longtext,
	PRIMARY KEY (ckey)
) DEFAULT CHARSET=utf8;
create table if not exists cache_table(
	ckey varchar(64) not null,
	cdata longtext,
	PRIMARY KEY (ckey)
) DEFAULT CHARSET=utf8;

