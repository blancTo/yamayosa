#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ TOPICS BOARD : admin.cgi - 2011/03/06
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

# 認証
&check_passwd;

# 処理分岐
if ($in{data_new}) { &data_new; }
if ($in{data_men}) { &data_men; }

# メニュー画面
&menu_html;

#-----------------------------------------------------------
#  メニュー画面
#-----------------------------------------------------------
sub menu_html {
	&header("メニューTOP");

	print <<EOM;
<div align="center">
<p>選択ボタンを押してください。</p>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<table border="1" cellpadding="5" cellspacing="0" class="menu">
<tr>
	<th>選択</th>
	<th width="280">処理メニュー</th>
</tr><tr>
	<td><input type="submit" name="data_new" value="選択"></td>
	<td>新規記事作成</td>
</tr><tr>
	<td><input type="submit" name="data_men" value="選択"></td>
	<td>記事メンテナンス（修正・削除）</td>
</tr><tr>
	<td><input type="button" value="選択" onclick="javascript:window.location='$cf{bbs_cgi}'"></td>
	<td>掲示板へ移動</td>
</tr><tr>
	<td><input type="button" value="選択" onclick="javascript:window.location='$cf{admin_cgi}'"></td>
	<td>ログアウト</td>
</tr>
</table>
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  新規記事
#-----------------------------------------------------------
sub data_new {
	# 新規作成実行
	if ($in{job} eq 'new2') { &add_data; }

	# 編集時
	my ($no,$date,$sub,$com,$e1,$w1,$h1,$e2,$w2,$h2,$e3,$w3,$h3,$tag,$clip,$tube) = @_;

	# タグ指定
	my $checked;
	if ($tag == 1) {
		$com =~ s/<br>/<br>\n/ig;
		$checked = "checked";
	} else {
		$com =~ s/<br>/\n/ig;
		$checked = "";
	}
	# 添付
	my %chk;
	if ($clip eq 't') {
		$chk{y} = "checked";
		$chk{i} = "";
	} else {
		$chk{y} = "";
		$chk{i} = "checked";
	}

	# パラメータ定義
	my $job = $in{job} ? "edit2" : "new2";

	# 新規投稿時は年月日を取得
	my ($hidden,$md);
	if ($in{data_new}) {
		$ENV{TZ} = "JST-9";
		my ($mday,$mon,$year) = (localtime(time))[3..5];
		$date = sprintf("%04d/%02d/%02d", $year+1900,$mon+1,$mday);
		$hidden = qq|<input type="hidden" name="data_new" value="1">|;
	} else {
		$hidden = qq|<input type="hidden" name="data_men" value="1">|;
		$md = 'data_men';
	}

	# フォーム表示
	&header("投稿フォーム", "js");
	&back_btn($md);
	print <<"EOM";
<span class="ttl">■投稿フォーム</span>
<hr class="ttl" size="1">
<ul>
<li>HTMLタグを有効にする場合改行は無効となるため、改行する部分で &lt;br&gt; と記述すること。
<li>画像またはYouTubeタグ（ニコ動画等も可）を添付することができます（任意）。
</ul>
<form action="$cf{admin_cgi}" method="post" enctype="multipart/form-data">
<input type="hidden" name="pass" value="$in{pass}">
$hidden
<input type="hidden" name="job" value="$job">
<input type="hidden" name="no" value="$no">
<table border="1" cellpadding="5" cellspacing="0" class="form">
<tr>
	<th>年月日</th>
	<td><input type="text" name="date" value="$date" size="40"></td>
</tr><tr>
	<th>件名</th>
	<td><input type="text" name="sub" value="$sub" size="40"></td>
</tr><tr>
	<th>本文</th>
	<td><input type="checkbox" name="tag" value="1" $checked>HTMLタグ有効 (但し改行は無効)<br>
		<textarea name="comment" cols="50" rows="6">$com</textarea>
	</td>
</tr><tr>
	<th>添付</th>
	<td>
		<input type="radio" name="clip" value="i" onclick="entryChange1();" $chk{i}>画像
		<input type="radio" name="clip" value="t" onclick="entryChange1();" $chk{y}>YouTube
	</td>
</tr><tr id="ibox">
	<th>画像</th>
	<td nowrap>
EOM

	my %e = (1 => $e1, 2 => $e2, 3 => $e3);
	foreach my $i (1 .. 3) {
		print qq|画像$i : <input type="file" name="upfile$i" size="35">\n|;
		if ($e{$i}) {
			print qq|&nbsp;<input type="checkbox" name="del$i" value="1">削除\n|;
			print qq|[<a href="$cf{imgurl}/$no-$i$e{$i}" target="_blank">画像</a>]\n|;
		}
		print "<br>\n";
	}

	print <<EOM;
	</td>
</tr><tr id="ybox">
	<th>YouTube<br>タグ</th>
	<td><textarea name="tube" cols="50" rows="4">$tube</textarea></td>
</tr>
</table>
<br>
<input type="submit" value="送信する">
</form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  記事メンテナンス
#-----------------------------------------------------------
sub data_men {
	# 削除
	if ($in{job} eq "dele" && $in{no}) {

		my @data;
		open(DAT,"+< $cf{logfile}") or &error("open err: $cf{logfile}");
		while (<DAT>) {
			my ($no,$date,$sub,$com,$e1,$w1,$h1,$e2,$w2,$h2,$e3,$w3,$h3,$tag,$clip,$tube) = split(/<>/);
			if ($in{no} == $no) {
				unlink("$cf{imgdir}/$no-1$e1") if ($e1);
				unlink("$cf{imgdir}/$no-2$e2") if ($e2);
				unlink("$cf{imgdir}/$no-3$e3") if ($e3);
				next;
			}
			push(@data,$_);
		}
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);

	# 修正フォーム
	} elsif ($in{job} eq "edit" && $in{no}) {

		my @log;
		open(IN,"$cf{logfile}") or &error("open err: $cf{logfile}");
		while (<IN>) {
			my ($no,$date,$sub,$com,$e1,$w1,$h1,$e2,$w2,$h2,$e3,$w3,$h3,$tag,$clip,$tube) = split(/<>/);
			if ($in{no} == $no) {
				@log = ($no,$date,$sub,$com,$e1,$w1,$h1,$e2,$w2,$h2,$e3,$w3,$h3,$tag,$clip,$tube);
				last;
			}
		}
		close(IN);

		# 修正画面
		&data_new(@log);

	# 修正実行
	} elsif ($in{job} eq "edit2" && $in{no}) {

		# 入力チェック
		&input_check;
		$in{tube} =~ s/<br>//g;

		# コード変換
		Jcode::convert(\$in{sub}, 'sjis');
		Jcode::convert(\$in{comment}, 'sjis');

		# 画像アップ
		my ($e1n,$w1n,$h1n,$e2n,$w2n,$h2n,$e3n,$w3n,$h3n);
		if ($in{upfile1} || $in{upfile2} || $in{upfile3}) {
			($e1n,$w1n,$h1n,$e2n,$w2n,$h2n,$e3n,$w3n,$h3n) = &upload($in{no});
		}

		my @data;
		open(DAT,"+< $cf{logfile}") or &error("open err: $cf{logfile}");
		while (<DAT>) {
			chomp;
			my ($no,$date,$sub,$com,$e1,$w1,$h1,$e2,$w2,$h2,$e3,$w3,$h3,$tag,$clip,$tube) = split(/<>/);

			if ($in{no} == $no) {

				# 画像削除のとき
				if ($in{del1}) {
					unlink("$cf{imgdir}/$no-1$e1");
					$e1 = $w1 = $h1 = "";
				}
				if ($in{del2}) {
					unlink("$cf{imgdir}/$no-2$e2");
					$e2 = $w2 = $h2 = "";
				}
				if ($in{del3}) {
					unlink("$cf{imgdir}/$no-3$e3");
					$e3 = $w3 = $h3 = "";
				}
				# 画像差替（拡張子が異なる場合）
				if ($e1n && $e1n ne $e1) { unlink("$cf{imgdir}/$no-1$e1"); }
				if ($e2n && $e2n ne $e2) { unlink("$cf{imgdir}/$no-2$e2"); }
				if ($e3n && $e3n ne $e3) { unlink("$cf{imgdir}/$no-3$e3"); }

				# 画像差替
				if ($e1n) { $e1 = $e1n; $w1 = $w1n; $h1 = $h1n; }
				if ($e2n) { $e2 = $e2n; $w2 = $w2n; $h2 = $h2n; }
				if ($e3n) { $e3 = $e3n; $w3 = $w3n; $h3 = $h3n; }

				$_ = "$no<>$in{date}<>$in{sub}<>$in{comment}<>$e1<>$w1<>$h1<>$e2<>$w2<>$h2<>$e3<>$w3<>$h3<>$in{tag}<>$in{clip}<>$in{tube}<>";
			}
			push(@data,"$_\n");
		}
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);

	# ソート
	} elsif ($in{job} eq "sort") {

		my (@sort,@data);
		open(DAT,"+< $cf{logfile}") or &error("open err: $cf{logfile}");
		while (<DAT>) {
			my ($no,$date,$sub,$com,$e1,$w1,$h1,$e2,$w2,$h2,$e3,$w3,$h3,$tag,$clip,$tube) = split(/<>/);

			push(@sort,$in{"sort:$no"});
			push(@data,$_);
		}

		# ソート
		@data = @data[sort {$sort[$a] <=> $sort[$b]} 0 .. $#sort];

		# 更新
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);
	}

	&header("メニュー &gt; 記事メンテナンス");
	&back_btn();
	print <<"EOM";
<span class="ttl">■記事メンテナンス</span>
<hr class="ttl" size="1">
<ul>
<li>処理を選択して送信ボタンを押してください。
<li>並び替えは「ソ\ート」を選択し、順番の数字を変更して送信ボタンを押してください。
</ul>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="data_men" value="1">
処理：
<select name="job">
<option value="edit">修正
<option value="sort">ソ\ート
<option value="dele">削除
</select>
<input type="submit" value="送信する">
<p>
<table border="1" cellpadding="2" cellspacing="0" class="menu">
<tr>
  <th nowrap>選択</th>
  <th nowrap>順番</th>
  <th nowrap>タイトル</th>
  <th nowrap>日付</th>
  <th nowrap>画像</th>
</tr>
EOM

	# ログ展開
	my $i = 0;
	open(IN,"$cf{logfile}") || &error("open err: $cf{logfile}");
	while (<IN>) {
		my ($no,$date,$sub,$com,$e1,$w1,$h1,$e2,$w2,$h2,$e3,$w3,$h3,$tag,$clip,$tube) = split(/<>/);
		$i++;

		print qq|<tr><td><input type="radio" name="no" value="$no"></td>|;
		print qq|<td><input type="text" name="sort:$no" value="$i" size="3"></td>|;
		print qq|<td><b>$sub</b></td>|;
		print qq|<td nowrap>$date</td><td>|;
		print qq|[<a href="$cf{imgurl}/$no-1$e1">1</a>]\n| if ($e1);
		print qq|[<a href="$cf{imgurl}/$no-2$e2">2</a>]\n| if ($e2);
		print qq|[<a href="$cf{imgurl}/$no-3$e3">3</a>]\n| if ($e3);
		print qq|<br></td></tr>\n|;
	}
	close(IN);

	print <<EOM;
</table>
</form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  記事追加
#-----------------------------------------------------------
sub add_data {
	# 入力チェック
	&input_check;
	$in{tube} =~ s/<br>//g;

	# コード変換
	Jcode::convert(\$in{sub}, 'sjis');
	Jcode::convert(\$in{comment}, 'sjis');

	# データオープン
	my ($num,@file);
	open(DAT,"+< $cf{logfile}") or &error("open err: $cf{logfile}");
	while (<DAT>) {
		my ($no) = (split(/<>/))[0];

		if ($num < $no) { $num = $no; }
		push(@file,$_);
	}

	# 採番
	$num++;

	# 画像アップ
	my ($e1,$w1,$h1,$e2,$w2,$h2,$e3,$w3,$h3);
	if ($in{upfile1} || $in{upfile2} || $in{upfile3}) {
		($e1,$w1,$h1,$e2,$w2,$h2,$e3,$w3,$h3) = &upload($num);
	}

	# 最大記事数調整
	while ( $cf{max} - 1 <= @file ) {
		my $del = pop(@file);
		my ($no,$date,$sub,$com,$e1,$w1,$h1,$e2,$w2,$h2,$e3,$w3,$h3,$tag,$clip,$tube) = split(/<>/, $del);
		unlink("$cf{imgdir}/$no-1$e1") if ($e1);
		unlink("$cf{imgdir}/$no-2$e2") if ($e2);
		unlink("$cf{imgdir}/$no-3$e3") if ($e3);
	}

	# 更新
	unshift(@file,"$num<>$in{date}<>$in{sub}<>$in{comment}<>$e1<>$w1<>$h1<>$e2<>$w2<>$h2<>$e3<>$w3<>$h3<>$in{tag}<>$in{clip}<>$in{tube}<>\n");
	seek(DAT, 0, 0);
	print DAT @file;
	truncate(DAT, tell(DAT));
	close(DAT);

	&message("新規記事を追加しました");
}

#-----------------------------------------------------------
#  画像アップロード
#-----------------------------------------------------------
sub upload {
	my $no = shift;

	my @ret;
	foreach my $i (1 .. 3) {
		# 拡張子取得
		my $ext;
		if ($cgi->param_filename("upfile$i") =~ /(\.jpe?g|\.png|\.gif)$/i) {
			$ext = $1;
		} else {
			push(@ret,('','',''));
			next;
		}
		$ext =~ tr/A-Z/a-z/;
		if ($ext eq '.jpeg') { $ext = '.jpg'; }

		# 添付ファイル定義
		my $upfile = "$cf{imgdir}/$no-$i$ext";

		# アップロード書き込み
		open(UP,"+> $upfile") or &error("up err: $upfile");
		binmode(UP);
		print UP $in{"upfile$i"};
		close(UP);

		chmod(0666,$upfile);

		# 画像サイズ取得
		my ($w, $h);
		if ($ext eq ".jpg") { ($w,$h) = &j_size($upfile); }
		elsif ($ext eq ".gif") { ($w,$h) = &g_size($upfile); }
		elsif ($ext eq ".png") { ($w,$h) = &p_size($upfile); }

		push(@ret,($ext,$w,$h));
	}

	return @ret;
}

#-----------------------------------------------------------
#  JPEGサイズ認識
#-----------------------------------------------------------
sub j_size {
	my $jpg = shift;

	my ($h, $w, $t);
	open(IMG,"$jpg");
	binmode(IMG);
	read(IMG, $t, 2);
	while (1) {
		read(IMG, $t, 4);
		my ($m, $c, $l) = unpack("a a n", $t);

		if ($m ne "\xFF") {
			$w = $h = 0;
			last;
		} elsif ((ord($c) >= 0xC0) && (ord($c) <= 0xC3)) {
			read(IMG, $t, 5);
			($h, $w) = unpack("xnn", $t);
			last;
		} else {
			read(IMG, $t, ($l - 2));
		}
	}
	close(IMG);

	return ($w, $h);
}

#-----------------------------------------------------------
#  GIFサイズ認識
#-----------------------------------------------------------
sub g_size {
	my $gif = shift;

	my $data;
	open(IMG,"$gif");
	binmode(IMG);
	sysread(IMG, $data, 10);
	close(IMG);

	if ($data =~ /^GIF/) { $data = substr($data, -4); }
	my $w = unpack("v", substr($data, 0, 2));
	my $h = unpack("v", substr($data, 2, 2));

	return ($w, $h);
}

#-----------------------------------------------------------
#  PNGサイズ認識
#-----------------------------------------------------------
sub p_size {
	my $png = shift;

	my $data;
	open(IMG,"$png");
	binmode(IMG);
	read(IMG, $data, 24);
	close(IMG);

	my $w = unpack("N", substr($data, 16, 20));
	my $h = unpack("N", substr($data, 20, 24));

	return ($w, $h);
}

#-----------------------------------------------------------
#  HTMLヘッダー
#-----------------------------------------------------------
sub header {
	my ($ttl,$js) = @_;

	print "Content-type: text/html\n\n";
	print <<EOM;
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=shift_jis">
<meta http-equiv="content-style-type" content="text/css">
<style type="text/css">
<!--
body,td,th { font-size:80%; background:#fff; }
table.menu th { background:#ccc; }
table.form th { background:#ccc; width:70px; }
.ttl { color:green; }
p.err { color:#dd0000; }
p.msg { color:#006400; }
table.myform {  }
-->
</style>
EOM

	if ($js eq 'js') {
		print <<JAVAS;
<script type="text/javascript">
// referer: http://5am.jp/javascript/form_change_javascript/
	function entryChange1(){
		radio = document.getElementsByName('clip') 
		if(radio[0].checked) {
			//フォーム
			document.getElementById('ibox').style.display = "";
			document.getElementById('ybox').style.display = "none";
		}else if(radio[1].checked) {
			//フォーム
			document.getElementById('ibox').style.display = "none";
			document.getElementById('ybox').style.display = "";
		}
	}
	//オンロードさせ、リロード時に選択を保持
	window.onload = entryChange1;
</script>
JAVAS
	}

	print <<EOM;
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
#  エラー
#-----------------------------------------------------------
sub error {
	my $err = shift;

	&header("ERROR!");
	print <<EOM;
<div align="center">
<hr width="350">
<h3>ERROR!</h3>
<p class="err">$err</p>
<hr width="350">
<form>
<input type="button" value="前画面に戻る" onclick="history.back()">
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  完了メッセージ
#-----------------------------------------------------------
sub message {
	my $msg = shift;

	&header("完了");
	print <<EOM;
<div align="center" style="margin-top:3em;">
<hr width="350">
<p class="msg">$msg</p>
<hr width="350">
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="submit" value="管理画面に戻る">
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  戻りボタン
#-----------------------------------------------------------
sub back_btn {
	my $mode = shift;

	print <<EOM;
<div align="right">
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
@{[ $mode ? qq|<input type="submit" name="$mode" value="&lt; 前画面">| : "" ]}
<input type="submit" value="&lt; メニュー">
</form>
</div>
EOM
}

#-----------------------------------------------------------
#  入力チェック
#-----------------------------------------------------------
sub input_check {
	my $err;
	if (!$in{date}) { $err .= "日付が未入力です<br>"; }
	if (!$in{sub}) { $err .= "タイトルが未入力です<br>"; }
	if (!$in{comment}) { $err .= "メッセージが未入力です<br>"; }
	&error($err) if ($err);

	# タグ復元
	if ($in{tag} == 1) {
		$in{comment} =~ s/<br>//g;
	}
}

