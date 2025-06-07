#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ TOPICS BOARD : topics.cgi - 2011/11/23
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib "./lib";
use CGI::Minimal;
use Jcode;

# 設定ファイル認識
require "./init.cgi";
my %cf = &init;

# データ受理
CGI::Minimal::max_read_size($cf{maxdata});
my $cgi = CGI::Minimal->new;
&error('容量オーバー') if ($cgi->truncated);
my %in = &parse_form($cgi);

# 処理分岐
if ($in{mode} eq 'find') { &find_log; }
if ($in{poptag}) { &poptag; }
&bbs_list;

#-----------------------------------------------------------
#  記事表示
#-----------------------------------------------------------
sub bbs_list {
	# ページ数
	my $pg = $in{pg} || 0;

	# データ認識
	my ($i,@log);
	open(IN,"$cf{logfile}") or &error("open err: $cf{logfile}");
	while(<IN>) {
		$i++;
		next if ($i < $pg + 1);
		next if ($i > $pg + $cf{pg_max});

		push(@log,$_);
	}
	close(IN);

	# 繰越ボタン作成
	my $pg_btn = &make_pgbtn($i, $pg);

	# テンプレート読み込み
	open(IN,"$cf{tmpldir}/bbs.html") or &error("open err: bbs.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# テンプレート分割
	my ($head,$loop,$foot);
	if ($tmpl =~ /(.+)<!-- loop_begin -->(.+)<!-- loop_end -->(.+)/s) {
		($head,$loop,$foot) = ($1,$2,$3);
	} else {
		&error("テンプレートが不正です");
	}

	# 文字置換
	foreach ($head,$foot) {
		s/!bbs_title!/$cf{bbs_title}/g;
		s/!([a-z]+_cgi)!/$cf{$1}/g;
		s/!page_btn!/$pg_btn/g;
		s/!homepage!/$cf{homepage}/g;
	}

	# ヘッダ表示
	print "Content-type: text/html\n\n";
	print $head;

	# 記事展開
	foreach (@log) {
		my ($no,$date,$sub,$com,$e1,$w1,$h1,$e2,$w2,$h2,$e3,$w3,$h3,$tag,$clip,$tube) = split(/<>/);
		if ($tag == 1) {
			$com = &tag($com);
		} elsif ($cf{autolink}) {
			$com = &autolink($com);
		}

		# YouTube
		my $att;
		if ($clip eq 't') {
			$att = &tag($tube) if ($tube);

		# 画像
		} else {
			if ($e1) {
				my ($w,$h) = &resize($w1,$h1);
				$att .= qq|<a href="$cf{imgurl}/$no-1$e1" target="_blank"><img src="$cf{imgurl}/$no-1$e1" width="$w" height="$h" class="img"></a>\n|;
			}
			if ($e2) {
				my ($w,$h) = &resize($w2,$h2);
				$att .= qq|<a href="$cf{imgurl}/$no-2$e2" target="_blank"><img src="$cf{imgurl}/$no-2$e2" width="$w" height="$h" class="img"></a>\n|;
			}
			if ($e3) {
				my ($w,$h) = &resize($w3,$h3);
				$att .= qq|<a href="$cf{imgurl}/$no-3$e3" target="_blank"><img src="$cf{imgurl}/$no-3$e3" width="$w" height="$h" class="img"></a>\n|;
			}
		}

		# 文字置換
		my $tmp = $loop;
		$tmp =~ s/!date!/$date/g;
		$tmp =~ s/!subject!/$sub/g;
		$tmp =~ s/!comment!/$com/g;
		$tmp =~ s/<!-- clip -->/$att/g;
		print $tmp;
	}

	# フッタ（著作権表記は削除・改変を禁止）
	my $copy = &copyright;
	if ($foot =~ /(.+)(<\/body[^>]*>.*)/si) {
		print "$1$copy$2\n";
	} else {
		print "$foot$copy\n";
		print "</body></html>\n";
	}
	exit;
}

#-----------------------------------------------------------
#  ワード検索
#-----------------------------------------------------------
sub find_log {
	# 条件
	$in{cond} =~ s/\D//g;

	# 検索条件プルダウン
	my %op = (1 => 'AND', 0 => 'OR');
	my $op_cond;
	foreach (1,0) {
		if ($in{cond} eq $_) {
			$op_cond .= qq|<option value="$_" selected>$op{$_}\n|;
		} else {
			$op_cond .= qq|<option value="$_">$op{$_}\n|;
		}
	}

	# 検索実行
	Jcode::convert(\$in{word}, 'sjis');
	my @log = &search($in{word}, $in{cond}) if ($in{word} ne '');

	# テンプレート
	open(IN,"$cf{tmpldir}/find.html") or &error("open err: find.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# 分割
	$tmpl =~ /(.+)<!-- loop_begin -->(.+)<!-- loop_end -->(.+)/s;
	my ($head, $loop, $foot) = ($1, $2, $3);

	foreach ($head, $foot) {
		s/!bbs_cgi!/$cf{bbs_cgi}/g;
		s/<!-- op_cond -->/$op_cond/;
		s/!word!/$in{word}/;
	}

	# ヘッダ部
	print "Content-type: text/html\n\n";
	print $head;

	# ループ部
	foreach (@log) {
		my ($no,$date,$sub,$com,$e1,$w1,$h1,$e2,$w2,$h2,$e3,$w3,$h3,$tag,$clip,$tube) = split(/<>/);
		if ($tag == 1) {
			$com = &tag($com);
		} elsif ($cf{autolink}) {
			$com = &autolink($com);
		}

		# YouTube
		my $att;
		if ($clip eq 't') {
			if ($tube) {
				$att = qq|[<a href="$cf{bbs_cgi}?poptag=$no" target="pop" onclick="popup('!bbs_cgi!?poptag=$no')">埋込タグ</a>]|;
			}

		# 画像
		} else {
			if ($e1) {
				$att .= qq|[<a href="$cf{imgurl}/$no-1$e1" target="_blank">画像1</a>]\n|;
			}
			if ($e2) {
				$att .= qq|[<a href="$cf{imgurl}/$no-2$e2" target="_blank">画像2</a>]\n|;
			}
			if ($e3) {
				$att .= qq|[<a href="$cf{imgurl}/$no-3$e3" target="_blank">画像3</a>]\n|;
			}
		}
		if ($att) { $com .= "<p>$att</p>"; }

		my $tmp = $loop;
		$tmp =~ s/!sub!/$sub/g;
		$tmp =~ s/!date!/$date/g;
		$tmp =~ s/!comment!/$com/g;
		print $tmp;
	}

	# フッタ部
	if ($foot =~ /(.+)(<\/body[^>]*>.*)/si) {
		print "$1$cf{copyright}$2";
	} else {
		print "$foot$cf{copyright}";
		print "</body></html>\n";
	}
	exit;
}

#-----------------------------------------------------------
#  検索実行
#-----------------------------------------------------------
sub search {
	my ($word,$cond) = @_;

	# キーワードを配列化
	$word =~ s/　/ /g;
	my @wd = split(/\s+/, $word);

	# 検索処理
	my @log;
	open(IN,"$cf{logfile}") or &error("open err: $cf{logfile}");
	while (<IN>) {
		my ($no,$date,$nam,$eml,$sub,$com,$url,$hos,$pw,$tim) = split(/<>/);

		my $flg;
		foreach my $wd (@wd) {
			if (index("$nam $eml $sub $com $url", $wd) >= 0) {
				$flg++;
				if ($cond == 0) { last; }
			} else {
				if ($cond == 1) { $flg = 0; last; }
			}
		}
		next if (!$flg);

		push(@log,$_);
	}
	close(IN);

	# 検索結果
	return @log;
}

#-----------------------------------------------------------
#  ポップアップ埋込タグ
#-----------------------------------------------------------
sub poptag {
	$in{poptag} =~ s/\D//g;

	my $tube_tag;
	open(IN,"$cf{logfile}") or &error("open err: $cf{logfile}");
	while(<IN>) {
		my ($no,$date,$sub,$com,$e1,$w1,$h1,$e2,$w2,$h2,$e3,$w3,$h3,$tag,$clip,$tube) = split(/<>/);

		if ($in{poptag} == $no) {
			$tube_tag = $tube;
			last;
		}
	}
	close(IN);

	open(IN,"$cf{tmpldir}/poptag.html") or &error("open err: poptag.html");
	print "Content-type: text/html\n\n";
	while(<IN>) {
		s/!tag!/&tag($tube_tag)/eg;

		print;
	}
	close(IN);

	exit;
}

#-----------------------------------------------------------
#  画像リサイズ
#-----------------------------------------------------------
sub resize {
	my ($w,$h) = @_;

	# 画像表示縮小
	if ($w > $cf{max_img_w} || $h > $cf{max_img_h}) {
		my $w2 = $cf{max_img_w} / $w;
		my $h2 = $cf{max_img_h} / $h;
		my $key;
		if ($w2 < $h2) { $key = $w2; } else { $key = $h2; }
		$w = int ($w * $key) || 1;
		$h = int ($h * $key) || 1;
	}
	return ($w,$h);
}

#-----------------------------------------------------------
#  繰越ボタン作成
#-----------------------------------------------------------
sub make_pgbtn {
	my ($i,$pg) = @_;

	# ページ繰越定義
	my $next = $pg + $cf{pg_max};
	my $back = $pg - $cf{pg_max};

	# ページ繰越ボタン作成
	my $pg_btn;
	if ($back >= 0 || $next < $i) {
		$pg_btn .= "Page: ";

		my ($x, $y) = (1, 0);
		while ($i > 0) {
			if ($pg == $y) {
				$pg_btn .= qq(| <b>$x</b> );
			} else {
				$pg_btn .= qq(| <a href="$cf{bbs_cgi}?pg=$y">$x</a> );
			}
			$x++;
			$y += $cf{pg_max};
			$i -= $cf{pg_max};
		}
		$pg_btn .= "|";
	}
	return $pg_btn;
}

#-----------------------------------------------------------
#  著作権表記（削除・改変を禁ず）
#-----------------------------------------------------------
sub copyright {
	my $copy = <<EOM;
<p style="margin-top:3em;text-align:center;font-family:Verdana,Helvetica,Arial;font-size:10px;">
- <a href="http://www.kent-web.com/" target="_top">Topics Board</a> -
</p>
EOM
	return $copy;
}

#-----------------------------------------------------------
#  自動リンク
#-----------------------------------------------------------
sub autolink {
	local($_) = shift;

	s|(s?https?://[\w-.!~*'();/?:\@&=+\$,%#]+)|<a href="$1" target="_blank">$1</a>|g;
	$_;
}

#-----------------------------------------------------------
#  タグ復元
#-----------------------------------------------------------
sub tag {
	local($_) = @_;

	s/&lt;/</g;
	s/&gt;/>/g;
	s/&amp;/&/g;
	s/&quot;/"/g;
	$_;
}

