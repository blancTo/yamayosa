#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ LimeCounter : admin.cgi - 2011/09/28
#│ Copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib "./lib";
use Jcode;

# 外部ファイル取り込み
require './init.cgi';
my %cf = &init;

# データ受理
my %in = &parse_form;

# 認証
&check_passwd;

# 管理モード
&admin_mode;

#-----------------------------------------------------------
#  管理モード
#-----------------------------------------------------------
sub admin_mode {
	# 新規画面
	if ($in{job} eq "new") {

		&new_form;

	# 新規発行
	} elsif ($in{job} eq "new2") {

		if ($in{file} eq "http://") { $in{file} = ""; }
		if ($in{link} eq "http://") { $in{link} = ""; }
		if ($in{id} =~ /\W/) { &error("IDは英数字で指定してください"); }
		if ($in{id} eq "check") { &error("ID名でcheckは使用できません"); }
		if ($in{sub} eq "") { &error("タイトル名が未入力です"); }
		if ($cf{type} >= 2 && $in{file} eq "") {
			&error("ダウンロードファイルが未入力です");
		}

		# コード変換
		Jcode::convert(\$in{sub}, 'sjis');

		# indexチェック
		my ($flg,@data);
		open(DAT,"+< $cf{idxfile}") || &error("open err: $cf{idxfile}");
		while (<DAT>) {
			my ($id) = split(/<>/);

			if ($in{id} eq $id) {
				$flg++;
				last;
			}
			push(@data,$_);
		}

		# 重複
		if ($flg) {
			close(DAT);
			&error("$in{id}は既存のIDと重複しています");
		}

		# index更新
		seek(DAT, 0, 0);
		print DAT "$in{id}<>$in{sub}<>$in{link}<>$in{file}<>\n";
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);

		# カウンタ値
		open(OUT,"+> $cf{datadir}/$in{id}.dat") || &error("write err: $in{id}.dat");
		print OUT "$in{count}::\n";
		close(OUT);

	# 削除
	} elsif ($in{id} && $in{job} eq "dele") {

		# indexマッチング
		my @data;
		open(DAT,"+< $cf{idxfile}") || &error("Open Error: $cf{idxfile}");
		while (<DAT>) {
			my ($id) = split(/<>/);

			next if ($in{id} eq $id);

			push(@data,$_);
		}

		# index更新
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);

		# ログ削除
		unlink("$cf{datadir}/$in{id}.dat");

	# 修正画面
	} elsif ($in{id} && $in{job} eq "edit") {

		my ($id,$sub,$link,$file);

		# indexチェック
		open(IN,"$cf{idxfile}") || &error("Open Error: $cf{idxfile}");
		while (<IN>) {
			($id,$sub,$link,$file) = split(/<>/);

			if ($in{id} eq $id) { last; }
		}
		close(IN);

		&edit_form($id,$sub,$link,$file);

	# 修正実行
	} elsif ($in{id} && $in{job} eq "edit2") {

		if ($in{file} eq "http://") { $in{file} = ""; }
		if ($in{link} eq "http://") { $in{link} = ""; }
		if ($in{sub} eq "") { &error("タイトル名が未入力です"); }
		if ($cf{type} >= 2 && $in{file} eq "") {
			&error("ダウンロードファイルが未入力です");
		}

		# コード変換
		Jcode::convert(\$in{sub}, 'sjis');

		# index差替え
		my @data;
		open(DAT,"+< $cf{idxfile}") || &error("open err: $cf{idxfile}");
		while (<DAT>) {
			my ($id) = split(/<>/);

			if ($in{id} eq $id) {
				$_ = "$in{id}<>$in{sub}<>$in{link}<>$in{file}<>\n";
			}
			push(@data,$_);
		}
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);

		# カウンタ更新
		if ($in{cnt} != $in{count}) {
			open(DAT,"+< $cf{datadir}/$in{id}.dat");
			eval "flock(DAT, 2);";
			my $count = <DAT>;
			my ($count, $ip) = split(/:/, $count);

			seek(DAT, 0, 0);
			print DAT "$in{count}:$ip";
			truncate(DAT, tell(DAT));
			close(DAT);
		}
	}

	&header("管理モード");
	print <<EOM;
<form action="$cf{admin_cgi}">
<input type="submit" value="▲ログアウト">
</form>
<ul>
<li>処理を選択して送信ボタンを押してください。
</ul>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
処理： <select name="job">
<option value="new">新規
<option value="edit">修正
<option value="dele">削除
</select>
<input type="submit" value="送信する">
<dl>
EOM

	# index展開
	open(IN,"$cf{idxfile}") || &error("open err: $cf{idxfile}");
	while (<IN>) {
		my ($id,$sub,$link,$file) = split(/<>/);

		# カウンタ読み取り
		open(DB,"$cf{datadir}/$id.dat");
		my $count = <DB>;
		close(DB);

		my ($count,$ip) = split(/:/, $count);

		# 桁区切り
		$count = &comma($count);

		print qq|<dt><hr><input type="radio" name="id" value="$id"><b>$id</b>\n|;
		print qq|<dd>[タイトル] $sub &nbsp; [カウンタ] $count\n|;

		print "<dd>[リンク先] <a href=\"$link\">$link</a>\n" if ($link);
		print "<dd>[ファイル] <a href=\"$file\">$file</a>\n" if ($file);
	}
	close(IN);

	print <<EOM;
<dt><hr>
</dl>
</form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  新規画面
#-----------------------------------------------------------
sub new_form {
	&header("新規ID発行");
	print <<EOM;
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="submit" value="&lt; 前に戻る">
</form>
<ul>
<li>新規にID情報を発行します。
<li>ID名は任意の英数字で指定してください。大文字と小文字は別物として扱われます。
</ul>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="mode" value="admin">
<input type="hidden" name="job" value="new2">
ID名<br>
<input type="text" name="id" value="" size="10"> （英数字で指定）<br>
タイトル名<br>
<input type="text" name="sub" value="" size="30"><br>
カウンタ値<br>
<input type="text" name="count" value="0" size=10><br>
EOM

	if ($cf{type} >= 2) {
		print qq|ダウンロードファイル<br>\n|;
		print qq|<input type="text" name="file" value="http://" size="50"><br>\n|;
	}

	print <<EOM;
リストにリンクするページ（任意）<br>
<input type="text" name="link" value="http://" size="50">
<p>
<input type="submit" value="送信する"></form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  編集画面
#-----------------------------------------------------------
sub edit_form {
	my ($id,$sub,$link,$file) = @_;
	$link ||= 'http://';
	$file ||= 'http://';

	# カウンタ読み込み
	open(DB,"$cf{datadir}/$in{id}.dat");
	my $data = <DB>;
	close(DB);

	# 分解
	my ($count, $ip) = split(/:/, $data);

	# フォーム表示
	&header("ID編集");
	print <<"EOM";
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="submit" value="&lt; 前に戻る">
</form>
<ul>
<li><b>$id</b>の編集を行います。
<li>修正する部分のみ変更し送信ボタンを押してください。
</ul>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="mode" value="admin">
<input type="hidden" name="job" value="edit2">
<input type="hidden" name="cnt" value="$count">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="id" value="$in{id}">
タイトル名<br>
<input type="text" name="sub" value="$sub" size="30"><br>
カウンタ値<br>
<input type="text" name="count" value="$count" size="10"><br>
EOM

	if ($cf{type} >= 2) {
		print "ダウンロードファイル<br>\n";
		print "<input type=text name=file value=\"$file\" size=50><br>\n";
	}

	print <<EOM;
リストにリンクするページ（任意）<br>
<input type="text" name="link" value="$link" size="50">
<p>
<input type="submit" value="送信する"></form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  フォームデコード
#-----------------------------------------------------------
sub parse_form {
	my ($buf,%in);
	if ($ENV{REQUEST_METHOD} eq "POST") {
		&error('受理できません') if ($ENV{CONTENT_LENGTH} > $cf{maxdata});
		read(STDIN, $buf, $ENV{CONTENT_LENGTH});
	} else {
		$buf = $ENV{QUERY_STRING};
	}
	foreach ( split(/&/, $buf) ) {
		my ($key,$val) = split(/=/);
		$val =~ tr/+/ /;
		$val =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("H2", $1)/eg;

		# 無効化
		$val =~ s/&/&amp;/g;
		$val =~ s/</&lt;/g;
		$val =~ s/>/&gt;/g;
		$val =~ s/"/&quot;/g;
		$val =~ s/'/&#39;/g;
		$val =~ s/[\r\n]//g;

		$in{$key} .= "\0" if (defined($in{$key}));
		$in{$key} .= $val;
	}
	return %in;
}

#-----------------------------------------------------------
#  HTMLヘッダー
#-----------------------------------------------------------
sub header {
	my $ttl = shift;

	print "Content-type: text/html\n\n";
	print <<EOM;
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=shift_jis">
<meta http-equiv="content-style-type" content="text/css">
<style type="text/css">
<!--
body,td,th { font-size:80%; background:#f0f0f0; }
.ttl { color:#004040; }
p.err { color:#dd0000; }
p.msg { color:#006400; }
-->
</style>
<title>$ttl</title>
</head>
<body>
EOM
}

#-----------------------------------------------------------
#  パスワード認証
#-----------------------------------------------------------
sub check_passwd {
	# パスワードが未入力の場合は入力フォーム画面
	if ($in{pass} eq "") {
		&enter_form;

	# パスワード認証
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
<div align="center">
<form action="$cf{admin_cgi}" method="post">
<table width="380" style="margin-top:50px">
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
<script language="javascript">
<!--
self.document.forms[0].pass.focus();
//-->
</script>
</div>
</body>
</html>
EOM
	exit;
}


#-----------------------------------------------------------
#  エラー処理
#-----------------------------------------------------------
sub error {
	my $err =shift;

	&header("ERROR!");
	print <<EOM;
<div align="center">
<h3>ERROR !</h3>
<p><font color="#dd0000">$err</font></p>
<form>
<input type="button" value="前画面に戻る" onclick="history.back()">
</form>
</div>
</body>
</html>
EOM
	exit;
}
