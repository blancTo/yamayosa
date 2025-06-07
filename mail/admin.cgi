#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ Clip Mail : admin.cgi - 2011/10/29
#│ copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール実行
use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib './lib';
use CGI::Minimal;

# 外部ファイル取り込み
require './init.cgi';
my %cf = &init;

# データ受理
CGI::Minimal::max_read_size($cf{maxdata});
my $cgi = CGI::Minimal->new;
&error('容量オーバー') if ($cgi->truncated);

# フォームデコード
my %in = &parse_form;

# 基本処理
&pwd_check;
&menu_list;

#-----------------------------------------------------------
#  ログダウンロード
#-----------------------------------------------------------
sub menu_list {
	# ダウンロード実行
	if ($in{downld}) {

		# 選択チェック
		if (!$in{br}) { &error("オプションに未選択があります"); }

		# 改行コード定義
		my %br = ( win => "\r\n", mac => "\r", unix => "\n" );

		# ログをオープン
		my ($i, @item, %key, %head, %csv);
		open(IN,"$cf{logfile}") or &error("open err: $cf{logfile}");
		while(<IN>) {
			chomp;
			$i++;
			my @log = split(/<>/);

			my $csv;
			foreach my $n (0 .. $#log) {
				my ($key,$val) = split(/=/, $log[$n]);

				if ($n <= 1) {
					$head{$i} .= "$val,";
					next;
				}

				if (!defined($key{$key})) {
					$key{$key}++;
					push(@item,$key);
				}

				# HTML変換
				$val =~ s/&lt;/</g;
				$val =~ s/&gt;/>/g;
				$val =~ s/&quot;/"/g;
				$val =~ s/&#39;/'/g;
				$val =~ s/&amp;/&/g;

				$csv{"$i<>$key"} = $val;
			}
		}
		close(IN);

		# ダウンロード用ヘッダー
		print "Content-type: application/octet-stream\n";
		print "Content-Disposition: attachment; filename=data.csv\n\n";
		binmode(STDOUT);

		# 項目
		print qq|日付,IPアドレス,|, join(',', @item), $br{$in{br}};

		# CSV
		foreach (1 .. $i) {
			my $csv;
			foreach my $key (@item) {
				$csv .= qq|$csv{"$_<>$key"},|;
			}
			$csv =~ s/,$//;

			print "$head{$_}$csv$br{$in{br}}";
		}

		exit;
	}

	# ログ個数を数える
	my $i = 0;
	open(IN,"$cf{logfile}");
	++$i while(<IN>);
	close(IN);

	# ダウンロード画面
	&header("CSVダウンロード");
	&back_button;
	print <<EOM;
<blockquote>
・ 現在のログ個数： <b>$i</b>個<br>
・ 改行を選択して、ダウンロードボタンを押してください。<br>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<table cellspacing="1" class="menu">
<tr>
	<th class="item">改行形式</th>
	<td class="btn">
		<input type="radio" name="br" value="win">Windows形式 （CR+LF）<br>
		<input type="radio" name="br" value="mac">Macintosh形式 （CR）<br>
		<input type="radio" name="br" value="unix">UNIX形式 （LF）
	</td>
</tr>
</table>
<p></p>
<input type="submit" name="downld" value="ダウンロード">
</form>
</blockquote>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  認証
#-----------------------------------------------------------
sub pwd_check {
	# 入室画面
	if ($in{pass} eq "") {
		&enter_form;

	# 認証
	} elsif ($in{pass} ne $cf{password}) {
		&error("認証できません");
	}
}

#-----------------------------------------------------------
#  入室画面
#-----------------------------------------------------------
sub enter_form {
	&header("入室画面");
	print <<EOM;
<blockquote>
<form action="$cf{admin_cgi}" method="post">
<table width="380">
<tr>
	<td height="40" align="center">
		<fieldset><legend>管理パスワード入力</legend><br>
		<input type="password" name="pass" value="" size="20">
		<input type="submit" value=" 認証 "><br><br>
		</fieldset>
	</td>
</tr>
</table>
</form>
</blockquote>
<script language="javascript">
<!--
self.document.forms[0].pass.focus();
//-->
</script>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  HTMLヘッダ
#-----------------------------------------------------------
sub header {
	my $ttl = shift;

	print "Content-type: text/html\n\n";
	print <<"EOM";
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html lang="ja">
<head>
<meta http-equiv="content-type" content="text/html; charset=shift_jis">
<meta http-equiv="content-style-type" content="text/css">
<style type="text/css">
<!--
body,td,th { font-size: 80%; }
table.head { width:100%; background:#8080c0; }
td.obi { padding:7px; color:#fff; font-weight:bold; }
table.menu { width:350px; background:#8080c0; }
th.item { background:#c8c8e3; padding:8px 3px; white-space:nowrap; }
td.btn, th.btn { background:#fff; padding:8px 3px; white-space:nowrap; }
.wid-300 { width:300px; }
p.red { color:#dd0000; }
-->
</style>
<title>$ttl</title>
</head>
<table class="head">
<tr>
	<td class="obi">$ttl</td>
</tr>
</table>
EOM
}

#-----------------------------------------------------------
#  エラー処理
#-----------------------------------------------------------
sub error {
	my $err = shift;

	&header("ERROR");
	print <<EOM;
<blockquote>
<h3>ERROR !</h3>
<p class="red">$err<p>
<form>
<input type="button" value="前画面に戻る" onclick="history.back()">
</form>
</blockquote>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  ログアウト
#-----------------------------------------------------------
sub back_button {
	print <<EOM;
<div style="text-align:right;">
<form action="$cf{admin_cgi}">
<input type="submit" value="× LOGOUT">
</form>
</div>
EOM
}

#-----------------------------------------------------------
#  フォームデコード
#-----------------------------------------------------------
sub parse_form {
	my %in;
	foreach ( $cgi->param() ) {
		my $val = $cgi->param($_);

		$val =~ s/&/&amp;/g;
		$val =~ s/</&lt;/g;
		$val =~ s/>/&gt;/g;
		$val =~ s/"/&quot;/g;
		$val =~ s/'/&#39;/g;
		$val =~ s/[\r\n]/\t/g;

		$in{$_} = $val;
	}
	return %in;
}

