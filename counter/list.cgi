#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ LimeCounter : list.cgi - 2011/09/28
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);

# 外部ファイル取り込み
require './init.cgi';
my %cf = &init;

# 処理分岐
&list_data;

#-----------------------------------------------------------
#  集計画面
#-----------------------------------------------------------
sub list_data {
	# データ読み込み
	my $all = 0;
	my (@data,@sort);
	open(IN,"$cf{idxfile}") or &error("open err: $cf{idxfile}");
	while (<IN>) {
		my ($id,$sub,$link,$file) = split(/<>/);

		open(DB,"$cf{datadir}/$id.dat");
		my $data = <DB>;
		close(DB);

		# ログ分解
		my ($count, $ip) = split(/:/, $data);

		# 総計
		$all += $count;

		push(@sort,$count);
		push(@data,"$id<>$sub<>$link<>$count");
	}
	close(IN);

	# ソート処理
	@data = @data[sort {$sort[$b] <=> $sort[$a]} 0 .. $#sort];

	# テンプレート読込
	open(IN,"$cf{list_tmpl}") or &error("open err: $cf{list_tmpl}");
	my $tmpl = join('', <IN>);
	close(IN);

	# テンプレート分解
	$tmpl =~ /(.+)<!-- loop_begin -->(.+)<!-- loop_end -->(.+)/s;
	my ($head, $loop, $foot) = ($1, $2, $3);
	$head =~ s/!homepage!/$cf{homepage}/g;

	# 画面展開
	print "Content-type: text/html\n\n";
	print $head;

	# 集計結果展開
	my ($i,$rk,$bef_c,$bef_r);
	foreach (@data) {
		my ($id,$item,$link,$count) = split(/<>/);
		$item = qq|<a href="$link" target="_blank">$item</a>| if ($link);
		$i++;

		my ($per,$wid);
		if ($all > 0) {
			$per = sprintf("%.1f", $count * 100 / $all);
			if ($per > 100) { $per = 100; }
			$wid = int($per * 5);
			if ($wid < 1) { $wid = 1; }
		} else {
			$per = "0.0";
			$wid = 1;
		}

		# 順位定義
		if ($count ne $bef_c) { $rk = $i; } else { $rk = $bef_r; }
		$bef_c = $count;
		$bef_r = $rk;

		# 文字置き換え
		my $tmp = $loop;
		$tmp =~ s/!item!/$item/g;
		$tmp =~ s/!rank!/$rk/g;
		$tmp =~ s/!count!/&comma($count)/eg;
		$tmp =~ s|!graph!|<img src="$cf{graph}" height="8" width="$wid"> $per%|g;
		print $tmp;
	}

	# フッター
	$foot =~ s/!all!/&comma($all)/eg;
	&footer($foot);
}

#-----------------------------------------------------------
#  フッター
#-----------------------------------------------------------
sub footer {
	my $foot = shift;

	# 著作権表記（削除・改変禁止）
	my $copy = <<EOM;
<p style="margin-top:3em;text-align:center;font-family:Verdana,Helvetica,Arial;font-size:10px;">
- <a href="http://www.kent-web.com/" target="_top">LimeCounter</a> -
</p>
EOM

	if ($foot =~ /(.+)(<\/body[^>]*>.*)/si) {
		print "$1$copy$2\n";
	} else {
		print "$foot$copy\n";
		print "</body></html>\n";
	}
	exit;
}

