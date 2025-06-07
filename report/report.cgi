#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ アクセス解析システム
#│ Access Report : report.cgi - 2011/09/18
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
my $cgi = CGI::Minimal->new;

# 解析
&analyze;

#-----------------------------------------------------------
#  解析
#-----------------------------------------------------------
sub analyze {
	# ランダムモード
	if ($cf{rand} > 0) {
		srand;
		my $rand = int(rand($cf{rand}));
		if ($rand != 0) { &load_img; }
	}

	# リンク元取得
	my $ref;
	if ($cf{ssi}) {
		$ref = $ENV{HTTP_REFERER};
	} else {
		$ref = $ENV{QUERY_STRING};
	}

	# リンク元解析
	if ($ref =~ /^https?/i) {

		# URLデコード
		$ref = $cgi->url_decode($ref);

		# コード変換
		$ref = Jcode->new($ref)->sjis;

		# 無害化
		$ref = $cgi->htmlize($ref);
		$ref =~ s/['\r\n\0]//g;

	} else {
		$ref = '';
	}

	# リンク元集計での除外指定
	if ($cf{myurl}) {
		my $flg;
		foreach ( split(/\s+/, $cf{myurl}) ) {
			if (index($ref,$_) >= 0) { $flg++; last; }
		}
		if ($flg) { $ref = ''; }
	}

	# ブラウザ情報取得
	my $hua = $ENV{HTTP_USER_AGENT};

	my ($os,$agent);
	if ($hua =~ /AOL/) { $agent = 'AOL'; }
	elsif ($hua =~ /Opera/i) { $agent = 'Opera'; }
	elsif ($hua =~ /PlayStation/i) { $agent = 'PlayStation'; }
	elsif ($hua =~ /Googlebot/i) { $agent = 'Googlebot'; }
	elsif ($hua =~ /slurp\@inktomi\.com/i) { $agent = 'Slurp/cat'; }
	elsif ($hua =~ /Infoseek SideWinder/i) { $agent = 'Infoseek SideWinder'; }
	elsif ($hua =~ /FAST\-WebCrawler/i) { $agent = 'FAST-WebCrawler'; }
	elsif ($hua =~ /ia_archiver/i) { $agent = 'ia_archiver'; }
	elsif ($hua =~ /Chrome/i) { $agent = 'Chrome'; }
	elsif ($hua =~ /Safari/i) { $agent = 'Safari'; }
	elsif ($hua =~ /Firefox/i) { $agent = 'Firefox'; }
	elsif ($hua =~ /MSIE (\d+)/i) { $agent = "MSIE $1"; }
	elsif ($hua =~ /Netscape/i) { $agent = 'Netscape'; }
	elsif ($hua =~ /Mozilla/i) { $agent = 'Mozilla'; }
	elsif ($hua =~ /Gecko/i) { $agent = 'Gecko'; }
	elsif ($hua =~ /Lynx/i) { $agent = 'Lynx'; }
	elsif ($hua =~ /Cuam/i) { $agent = 'Cuam'; $os = 'Windows'; }
	elsif ($hua =~ /Ninja/i) { $agent = 'Ninja'; $os = 'Windows'; }
	elsif ($hua =~ /WWWC/i) { $agent = 'WWWC'; $os = 'Windows'; }
	elsif ($hua =~ /DoCoMo/i) { $agent = $os = 'DoCoMo'; }
	elsif ($hua =~ /^MOT-|^J-PHONE|^SoftBank|^Vodafone|NetFront/i) { $agent = $os = 'SoftBank'; }
	elsif ($hua =~ /^UP\.Browser|^KDDI/i) { $agent = $os = 'EZweb'; }
	elsif ($hua =~ /L\-mode/i) { $agent = $os = 'L-mode'; }
	elsif ($hua =~ /ASTEL/i) { $agent = $os = 'ASTEL'; }
	elsif ($hua =~ /PDXGW/i) { $agent = $os = 'H&quot;'; }

	$agent = $cgi->htmlize($agent) if ($agent);
	$agent =~ s/[\r\n\0]//g;

	if ($hua =~ /win[dows ]*95/i) { $os = 'Win95'; }
	elsif ($hua =~ /win[dows ]*9x/i) { $os = 'WinMe'; }
	elsif ($hua =~ /win[dows ]*98/i) { $os = 'Win98'; }
	elsif ($hua =~ /win[dows ]*XP/i) { $os = 'WinXP'; }
	elsif ($hua =~ /win[dows ]*NT ?5\.1/i) { $os = 'WinXP'; }
	elsif ($hua =~ /Win[dows ]*NT ?5/i) { $os = 'Win2000'; }
	elsif ($hua =~ /win[dows ]*2000/i) { $os = 'Win2000'; }
	elsif ($hua =~ /Win[dows ]*NT ?5\.2/i) { $os = 'Win2003'; }
	elsif ($hua =~ /Win[dows ]*NT 6\.0/i || $hua =~ /Vista/i) { $os = 'WinVista'; }
	elsif ($hua =~ /Win[dows ]*NT 6\.1/i) { $os = 'Win7'; }
	elsif ($hua =~ /Win[dows ]*NT/i) { $os = 'WinNT'; }
	elsif ($hua =~ /Win[dows ]*CE/i) { $os = 'WinCE'; }
	elsif ($hua =~ /shap pda browser/i) { $os = 'ZAURUS'; }
	elsif ($hua =~ /Mac/i) { $os = 'Mac'; }
	elsif ($hua =~ /X11|SunOS|Linux|HP-UX|FreeBSD|NetBSD|OSF1|IRIX/i) { $os = 'UNIX'; }

	# ホスト名を取得
	my $host = $ENV{REMOTE_HOST};
	my $addr = $ENV{REMOTE_ADDR};
	if ($host eq "" || $host eq $addr) {
		$host = gethostbyaddr(pack("C4",split(/\./,$addr)),2) || $addr;
	}

	if ($host =~ /(.*)\.(\d+)$/) { ; }
	elsif ($host =~ /(.*)\.(.*)\.(.*)\.(.*)$/) { $host = "\*\.$2\.$3\.$4"; }
	elsif ($host =~ /(.*)\.(.*)\.(.*)$/) { $host = "\*\.$2\.$3"; }

	# 時間取得
	$ENV{TZ} = "JST-9";
	my $hour = (localtime(time))[2];

	# ログ読み込み
	my @data;
	open(DAT,"+< $cf{logfile}") or die "open err: $cf{logfile}";
	eval 'flock(DAT, 2);';
	my $top = <DAT>;

	# IPチェック
	if ($cf{ip_chk}) {
		chomp($top);
		if ($addr eq $top) {
			close(DAT);
			&load_img;
		}
	}

	# 記事数を調整
	my $i = 0;
	while (<DAT>) {
		$i++;
		push(@data,$_);

		last if ($i >= $cf{maxlog} - 1);
	}

	# 更新
	seek(DAT, 0, 0);
	print DAT "$addr\n";
	print DAT "$agent<>$os<>$host<>$ref<>$hour<>\n";
	print DAT @data;
	truncate(DAT, tell(DAT));
	close(DAT);

	# 表示
	&load_img;
}

#-----------------------------------------------------------
#  結果表示
#-----------------------------------------------------------
sub load_img {
	if ($cf{ssi}) {
		print "Content-type: text/plain\n\n";
	} else {
		# 透過GIF定義
		my @img = qw(
			47 49 46 38 39 61 02 00 02 00 80
			00 00 00 00 00 ff ff ff 21 f9 04
			01 00 00 01 00 2c 00 00 00 00 02
			00 02 00 00 02 02 8c 53 00 3b
			);

		print "Content-type: image/gif\n\n";
		binmode (STDOUT);
		foreach (@img) {
			print pack('C*',hex($_));
		}
	}
	exit;
}

