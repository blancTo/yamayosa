#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ アクセス解析システム
#│ Access Report : check.cgi - 2011/08/25
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;

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

# ログファイルのチェック
if (-e $cf{logfile}) {
	print "<li>ログファイルのパス : OK\n";

	# パーミッション
	if (-r $cf{logfile} && -w $cf{logfile}) {
		print "<li>ログファイルのパーミッション : OK\n";
	} else {
		print "<li>ログファイルのパーミッション : NG\n";
	}
} else {
	print "<li>ログファイルのパス : NG\n";
}

print <<EOM;
</ul>
</body>
</html>
EOM
exit;


