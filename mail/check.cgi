#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ CLIP MAIL : check.cgi - 2011/10/29
#│ copyright (c) KentWeb
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
<li>Perlバージョン : $]
EOM

# sendmailチェック
print "<li>sendmailパス : ";
if (-e $cf{sendmail}) {
	print "OK\n";
} else {
	print "NG → $cf{sendmail}\n";
}

# テンプレート
my @tmpl = qw|conf.html err1.html err2.html thx.html mail.txt reply.txt|;
foreach (@tmpl) {
	print "<li>テンプレートパス ( $_ ) : ";

	if (-f "$cf{tmpldir}/$_") {
		print "OK\n";
	} else {
		print "NG\n";
	}
}

# 一時ディレクトリ
if (-d $cf{upldir}) {
	print "<li>一時ディレクトリパス : OK\n";

	if (-r $cf{upldir} && -w $cf{upldir} && -x $cf{upldir}) {
		print "<li>一時ディレクトリパーミッション : OK\n";
	} else {
		print "<li>一時ディレクトリパーミッション : NG\n";
	}

} else {
	print "<li>一時ディレクトリパス : NG\n";
}

# ログファイル
if (-f $cf{logfile}) {
	print "<li>ログファイルパス : OK\n";

	if (-r $cf{logfile} && -w $cf{logfile}) {
		print "<li>ログファイルパーミッション : OK\n";
	} else {
		print "<li>ログファイルパーミッション : NG\n";
	}
} else {
	print "<li>ログファイルパス : NG\n";
}

print <<EOM;
</ul>
</body>
</html>
EOM
exit;


