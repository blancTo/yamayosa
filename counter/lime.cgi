#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ LimeCounter : lime.cgi - 2011/07/14
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;

# 外部ファイル取り込み
require './init.cgi';
my %cf = &init;

# 外部データ受け取り
my $buf = $ENV{QUERY_STRING};
$buf =~ s/\W//g;
&error("ID情報不正") if ($buf eq '');

# データファイル定義
my $datafile = "$cf{datadir}/$buf.dat";

# カウントアップ
&count_up;

#-----------------------------------------------------------
#  カウント処理
#-----------------------------------------------------------
sub count_up {
	# IPアドレス取得
	my $addr = $ENV{REMOTE_ADDR};

	# データ読み取り
	open(DAT,"+< $datafile") || &error("open errr: $datafile");
	eval "flock(DAT, 2);";
	my $data = <DAT>;

	# データ分解
	my ($count, $ip) = split(/:/, $data);

	# カウントアップ
	if (!$cf{ip_chk} || ($cf{ip_chk} && $addr ne $ip)) {
		$count++;

		seek(DAT, 0, 0);
		print DAT "$count:$addr";
		truncate(DAT, tell(DAT));
	}
	close(DAT);

	# ページカウンタのとき
	if ($cf{type} == 1) {

		# ダミー画像
		my @gif = qw(
			47 49 46 38 39 61 02 00 02 00 80 00	00 00 00 00 ff ff ff
			21 f9 04 01 00 00 01 00 2c 00 00 00 00 02 00 02 00 00 02
			02 8c 53 00 3b
		);

		# ダミー画像表示
		print "Content-type: image/gif\n\n";
		foreach (@gif) {
			print pack('C*',hex($_));
		}
		exit;

	# ダウンロードカウンタのとき
	} else {

		# index読み取り
		my ($flg, $jump);
		open(IN,"$cf{idxfile}") || &error("open err: $cf{idxfile}");
		while (<IN>) {
			my ($id,$sub,$link,$file) = split(/<>/);

			if ($buf eq $id) {
				$flg++;
				$jump = $file;
				last;
			}
		}
		close(IN);

		if (!$flg) { &error("IDが不正です"); }

		# Locationヘッダ
		if ($cf{type} == 2) {

			# PerlIS対応
			if ($ENV{PERLXS} eq "PerlIS") {
				print "HTTP/1.0 302 Temporary Redirection\r\n";
 				print "Content-type: text/html\n";
			}

			# ファイルへ移動
			print "Location: $jump\n\n";
			exit;

		# metaタグ
		} else {
			&header("<meta http-equiv=\"refresh\" content=\"1; url=$jump\">");
			print qq|<div align="center">\n|;
			print qq|<p>ダウンロードできない場合は<a href="$jump">ここ</a>をクリック。</p>\n|;
			print qq|</div>\n|;
			print qq|</body></html>\n|;
			exit;
		}
	}
}

#-----------------------------------------------------------
#  エラー処理
#-----------------------------------------------------------
sub error {
	my $err = shift;

	# ダウンロードカウンタの場合
	if ($cf{type} > 1) {
		&header();
		print "<h3>ERROR</h3>\n";
		print "<p>$err</p>\n";
		print "</body></html>\n";
		exit;

	# ページカウンタの場合
	} else {
		die "error: $err";
	}
}

#-----------------------------------------------------------
#  HTMLヘッダ
#-----------------------------------------------------------
sub header {
	my ($meta) = @_;

	print "Content-type: text/html\n\n";
	print <<EOM;
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=shift_jis">
$meta
<title>$cf{version}</title>
</head>
<body>
EOM
}

