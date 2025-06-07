#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ LimeCounter : check.cgi - 2011/09/28
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);

# 外部ファイル取り込み
require './init.cgi';
my %cf = &init;

print <<EOM;
Content-type: text/html

<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=shift_jis">
<title>Check Mode</title>
</head>
<body>
<b>Check Mode: [ $cf{version} ]</b>
<ul>
EOM

# インデックスファイル
if (-f $cf{idxfile}) {
	print "<li>インデックスファイルパス : OK\n";
	if (-r $cf{idxfile} && -w $cf{idxfile}) {
		print "<li>インデックスファイルパーミッション : OK\n";
	} else {
		print "<li>インデックスファイルパーミッション : NG\n";
	}
} else {
	print "<li>インデックスファイルパス : NG\n";
}

# テンプレート
if (-f $cf{list_tmpl}) {
	print "<li>テンプレートパス : OK\n";
} else {
	print "<li>テンプレートパス : NG\n";
}

# データディレクトリ
if (-d $cf{datadir}) {
	print "<li>データディレクトリパス：OK\n";
	if (-r $cf{datadir} && -w $cf{datadir} && -x $cf{datadir}) {
		print "<li>データディレクトリパーミッション：OK\n";
	} else {
		print "<li>データディレクトリパーミッション : NG\n";
	}
} else {
	print "<li>データディレクトリパス : NG\n";
}


print <<EOM;
</ul>
</body>
</html>
EOM
exit;


