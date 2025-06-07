#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ アクセス解析システム
#│ Access Report : list.cgi - 2011/08/25
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);

# 設定ファイル認識
require "./init.cgi";
my %cf = &init;

# リスト一覧
&list_data;

#-----------------------------------------------------------
#  リスト一覧
#-----------------------------------------------------------
sub list_data {
	my ($count,%ag,%os,%hos,%ref,%hr,%i);
	open(IN,"$cf{logfile}") or die "open err";
	my $top = <IN>;
	while (<IN>) {
		$count++;
		my ($ag,$os,$hos,$ref,$hr) = split(/<>/);

		if ($ag) { $ag{$ag}++; $i{ag}++; }
		if ($os) { $os{$os}++; $i{os}++; }
		if ($hos) { $hos{$hos}++; $i{hos}++; }
		if ($ref) { $ref{$ref}++; $i{ref}++; }
		if ($hr ne '') { $hr{$hr}++; }
	}
	close(IN);

	# テンプレート読み込み
	open(IN,"$cf{tmpldir}/list.html") or die "open err";
	my $tmpl = join('', <IN>);
	close(IN);

	# 文字置き換え
	$tmpl =~ s/!homepage!/$cf{homepage}/g;
	$tmpl =~ s/!log!/$count/g;
	$tmpl =~ s/!(max_\w+)!/$cf{$1}/g;
	$tmpl =~ s/!get-ref!/$i{ref}/g;

	$tmpl =~ /(.+)<!-- loop:ref -->(.+)<!-- loop:ref -->(.+)<!-- loop:os -->(.+)<!-- loop:os -->(.+)<!-- loop:ag -->(.+)<!-- loop:ag -->(.+)<!-- loop:hos -->(.+)<!-- loop:hos -->(.+)/s;
	my ($head,$ref_loop,$ref_bot,$os_loop,$os_bot,$ag_loop,$ag_bot,$hos_loop,$foot) = ($1,$2,$3,$4,$5,$6,$7,$8,$9);

	print "Content-type: text/html\n\n";
	print $head;

	foreach ( sort{ $ref{$b} <=> $ref{$a} }keys(%ref) ) {
		last if ($ref{$_} < $cf{max_ref});

		my $per = int ( ($ref{$_}*1000 / $i{ref}) + 0.5 ) / 10;
		$per = sprintf("%.1f", $per);
		my $wid = int($per * 8) > 1 ? int($per * 8) : 1;

		my $tmp = $ref_loop;
		$tmp =~ s/!count!/$ref{$_}/g;
		$tmp =~ s|!url!|<a href="$_" target="_blank">$_</a>|g;
		$tmp =~ s|!graph!|<img src="$cf{graph1}" width="$wid" height="8"> $per%|g;
		print $tmp;
	}

	print $ref_bot;

	foreach ( sort{ $os{$b} <=> $os{$a} }keys(%os) ) {
		last if ($os{$_} < $cf{max_os});

		my $per = int ( ($os{$_}*1000 / $i{os}) + 0.5 ) / 10;
		$per = sprintf("%.1f", $per);
		my $wid = int($per * 8) > 1 ? int($per * 8) : 1;

		my $tmp = $os_loop;
		$tmp =~ s/!count!/$os{$_}/g;
		$tmp =~ s|!os!|$_|g;
		$tmp =~ s|!graph!|<img src="$cf{graph1}" width="$wid" height="8"> $per%|g;
		print $tmp;
	}

	print $os_bot;

	foreach ( sort{ $ag{$b} <=> $ag{$a} }keys(%ag) ) {
		last if ($ag{$_} < $cf{max_ag});

		my $per = int ( ($ag{$_}*1000 / $i{ag}) + 0.5 ) / 10;
		$per = sprintf("%.1f", $per);
		my $wid = int($per * 8) > 1 ? int($per * 8) : 1;

		my $tmp = $ag_loop;
		$tmp =~ s/!count!/$ag{$_}/g;
		$tmp =~ s|!agent!|$_|g;
		$tmp =~ s|!graph!|<img src="$cf{graph1}" width="$wid" height="8"> $per%|g;
		print $tmp;
	}

	print $ag_bot;

	foreach ( sort{ $hos{$b} <=> $hos{$a} }keys(%hos) ) {
		last if ($hos{$_} < $cf{max_hos});

		my $per = int ( ($hos{$_}*1000 / $i{hos}) + 0.5 ) / 10;
		$per = sprintf("%.1f", $per);
		my $wid = int($per * 8) > 1 ? int($per * 8) : 1;

		my $tmp = $hos_loop;
		$tmp =~ s/!count!/$hos{$_}/g;
		$tmp =~ s|!host!|$_|g;
		$tmp =~ s|!graph!|<img src="$cf{graph1}" width="$wid" height="8"> $per%|g;
		print $tmp;
	}

	# 時間帯
	$foot =~ s/!hr-(\d{1,2})!/&hour($hr{$1})/eg;

	# フッター
	&footer($foot);
}

#-----------------------------------------------------------
#  時間帯グラフ
#-----------------------------------------------------------
sub hour {
	my $hr = shift;
	$hr ||= 0;

	return qq|$hr<br><img src="$cf{graph2}" width="7" height="$hr">|;
}

#-----------------------------------------------------------
#  フッター
#-----------------------------------------------------------
sub footer {
	my $foot = shift;

	# 著作権表記（削除・改変禁止）
	my $copy = <<EOM;
<p style="margin-top:2em;text-align:center;font-family:Verdana,Helvetica,Arial;font-size:10px;">
- <a href="http://www.kent-web.com/" target="_top">Access Report</a> -
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

