CREATE DATABASE IF NOT EXISTS telnet_site DEFAULT CHARSET utf8 COLLATE utf8_general_ci;
use telnet_site;
\
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
	ckey varchar(1024) not null,
	cdata longtext,
	PRIMARY KEY (ckey)
) DEFAULT CHARSET=utf8;
create table if not exists messages_table(
	id int(16) primary key auto_increment,
	creation_date timestamp DEFAULT CURRENT_TIMESTAMP,
	text longtext
) DEFAULT CHARSET=utf8;

--create user telnetsite
--grant insert,delete,update,select on telnet_site.* to telnetsite
--set password for telnetsite=password('abcdef')

