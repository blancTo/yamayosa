#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ CLIP MAIL : clipmail.cgi - 2011/11/10
#│ copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール実行
use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib './lib';
use CGI::Minimal;
use Jcode;
use MIME::Base64;

# Jcode宣言
my $j = new Jcode;

# 外部ファイル取り込み
require './init.cgi';
my %cf = &init;

# データ受理
CGI::Minimal::max_read_size($cf{maxdata});
my $cgi = CGI::Minimal->new;
&error('容量オーバー') if ($cgi->truncated);
my ($key,$need,$in) = &parse_form;

# 禁止ワードチェック
if ($cf{no_wd}) {
	my $flg;
	foreach (@$key) {
		foreach my $wd ( split(/,/, $cf{no_wd}) ) {
			if (index($$in{$_},$wd) >= 0) {
				$flg++;
				last;
			}
		}
		if ($flg) { &error("禁止ワードが含まれています"); }
	}
}

# ホスト取得＆チェック
my ($host,$addr) = &get_host;

# 必須入力チェック
my ($check,@err,@need);
if ($$in{need} || @$need > 0) {

	# アンダーバーによる必須指定
	if (@$need > 0) {
		@need = @$need;
	}

	# needフィールドの値を必須配列に加える
	my @tmp = split(/\s+/, $$in{need});
	push(@need,@tmp);

	# 必須配列の重複要素を排除する
	my (@uniq,%seen);
	foreach (@need) {
		push(@uniq,$_) unless $seen{$_}++;
	}

	# 必須項目の入力値をチェックする
	foreach (@uniq) {

		# フィールドの値が投げられてこないもの（ラジオボタン等）
		if (!defined($$in{$_})) {
			$check++;
			push(@$key,$_);
			push(@err,$_);

		# 入力なしの場合
		} elsif ($$in{$_} eq "") {
			$check++;
			push(@err,$_);
		}
	}
}

# 入力内容マッチ
my ($match1,$match2);
if ($$in{match}) {
	($match1,$match2) = split(/\s+/, $$in{match}, 2);

	if ($$in{$match1} ne $$in{$match2}) {
		&error("$match1と$match2の再入力内容が異なります");
	}
}

# 入力チェック確認画面
if ($check) {
	&err_check($match2);
}

# E-mail書式チェック
if ($$in{email} =~ /\,/) {
	&error("メールアドレスにコンマ ( , ) が含まれています");
}
if ($$in{email} ne '' && $$in{email} !~ /^[\w\.\-]+\@[\w\.\-]+\.[a-zA-Z]{2,}$/) {
	&error("メールアドレスの書式が不正です");
}

# プレビュー
if ($$in{mode} ne "send") {
	&preview;

# 送信実行
} else {
	&send_mail;
}

#-----------------------------------------------------------
#  プレビュー
#-----------------------------------------------------------
sub preview {
	# 送信内容チェック
	&error("データを取得できません") if (@$key == 0);

	# 時間取得
	my $time = time;

	# 許可拡張子をハッシュ化
	my %ex;
	foreach ( split(/,/, $cf{extension}) ) {
		$ex{$_}++;
	}

	# 添付確認
	my ($err,@ext,%file,%ext);
	foreach (@$key) {
		if (/^clip-(\d+)$/) {
			my $num = $1;

			# ファイル名
			my $fname = $j->set($cgi->param_filename("clip-$1"))->euc;
			if ($fname =~ /([^\\\/:]+)\.([^\\\/:\.]+)$/) {

				# ファイル名
				$file{$num} = "$1.$2";
				$file{$num} = $j->set($file{$num},'euc')->sjis;

				# 拡張子チェック
				$ext{$num} = $2;
				$ext{$num} =~ tr/A-Z/a-z/;
				if (!defined($ex{$ext{$num}}) && $cf{extension}) {
					$err .= "$ext{$num},";
				}

				push(@ext,$num);
			}
		}
	}
	if ($err) {
		$err =~ s/,$//;
		&error("添付ファイルで許可されない拡張子があります → $err");
	}

	# 添付あり
	if (@ext > 0) {

		# 一時ディレクトリを掃除
		&clean_dir;

		# アップロード実行
		foreach my $i (@ext) {

			# ファイル定義
			my $upfile = "$cf{upldir}/$time-$i.$ext{$i}";

			# ファイル書き込み
			my $buf;
			open(UP,"+> $upfile") or &error("up err: $upfile");
			binmode(UP);
			print UP $$in{"clip-$i"};
			close(UP);
		}
	}

	# 画面展開
	open(IN,"$cf{tmpldir}/conf.html") or &error("open err: conf.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# テンプレート分割
	my ($head,$loop,$foot);
	if ($tmpl =~ /(.+)<!-- cell_begin -->(.+)<!-- cell_end -->(.+)/s) {
		($head,$loop,$foot) = ($1,$2,$3);
	} else {
		&error("テンプレートが不正です");
	}

	# 引数
	my $hidden .= qq|<input type="hidden" name="mode" value="send" />\n|;

	# 項目
	my ($bef,$item);
	foreach my $key (@$key) {
		next if ($bef eq $key);

		# 画像SUBMITボタンは無視
		next if ($key eq "x");
		next if ($key eq "y");
		if ($key eq "need" || $key eq "match" || ($$in{match} && $key eq $match2)) {
			next;
		}

		# 添付のとき
		if ($key =~ /^clip-(\d+)$/i) {

			my $no = $1;
			if (defined($file{$no})) {
				$hidden .= qq|<input type="hidden" name="$key" value="$file{$no}:$time-$no.$ext{$no}" />\n|;
			} else {
				$hidden .= qq|<input type="hidden" name="$key" value="" />\n|;
			}

			my $tmp = $loop;
			$tmp =~ s/!key!/添付$no/;

			# 画像のとき
			if ($ext{$no} =~ /^(gif|jpe?g|png|bmp)$/i && -B "$cf{upldir}/$time-$no.$ext{$no}") {

				# 表示サイズ調整
				my ($w,$h) = &resize("$cf{upldir}/$time-$no.$ext{$no}", $1);
				$tmp =~ s|!val!|<img src="$cf{uplurl}/$time-$no.$ext{$no}" width="$w" height="$h" alt="$file{$no}" />|;

			# 画像以外
			} else {
				$tmp =~ s/!val!/$file{$no}/;
			}
			$item .= $tmp;

		# テキスト（添付以外）
		} else {

#			$$in{$key} =~ s/\0/ /g;
			$hidden .= qq|<input type="hidden" name="$key" value="$$in{$key}" />\n|;

			# 改行変換
			$$in{$key} =~ s/\t/<br \/>/g;

			my $tmp = $loop;
			if (defined($cf{replace}->{$key})) {
				$tmp =~ s/!key!/$cf{replace}->{$key}/;
			} else {
				$tmp =~ s/!key!/$key/;
			}
			$tmp =~ s/!val!/$$in{$key}/;
			$item .= $tmp;
		}
		$bef = $key;
	}

	# 文字置換
	for ( $head, $foot ) {
		s/!mail_cgi!/$cf{mail_cgi}/g;
		s/<!-- hidden -->/$hidden/g;
	}

	# 画面展開
	print "Content-type: text/html\n\n";
	print $head, $item;

	# フッタ
	&footer($foot);
}

#-----------------------------------------------------------
#  送信実行
#-----------------------------------------------------------
sub send_mail {
	# 送信内容チェック
	&error("データを取得できません") if (@$key == 0);

	# 時間取得
	my ($date1, $date2) = &get_time;

	# ブラウザ情報
	my $agent = $ENV{HTTP_USER_AGENT};
	$agent =~ s/[<>&"'()+;]//g;

	# 本文テンプレ読み込み
	my $tbody;
	open(IN,"$cf{tmpldir}/mail.txt") or &error("open err: mail.txt");
	my $tbody = join('', <IN>);
	close(IN);

	# 改行
	$tbody =~ s/\r\n/\n/g;
	$tbody =~ s/\r/\n/g;

	# テンプレ変数変換
	$tbody =~ s/!date!/$date1/g;
	$tbody =~ s/!agent!/$agent/g;
	$tbody =~ s/!host!/$host/g;
	Jcode::convert(\$tbody, 'jis', 'sjis');

	# 自動返信ありのとき
	my $resbody;
	if ($cf{auto_res}) {

		# テンプレ
		open(IN,"$cf{tmpldir}/reply.txt") or &error("open err: reply.txt");
		$resbody = join('', <IN>);
		close(IN);

		# 改行
		$resbody =~ s/\r\n/\n/g;
		$resbody =~ s/\r/\n/g;

		# 変数変換
		$resbody =~ s/!date!/$date1/g;
		Jcode::convert(\$resbody, 'jis', 'sjis');
	}

	# ログファイルオープン
	open(DAT,"+< $cf{logfile}") or &error("open err: $cf{logfile}");
	eval "flock(DAT, 2);";

	# 先頭行を分解
	my $top_log = <DAT>;
	my ($log_date, $log_ip, $log_data) = split(/<>/, $top_log, 3);

	# ハッシュ%logに各項目を代入
	my %log;
	foreach ( split(/<>/, $log_data) ) {
		my ($key,$val) = split(/=/, $_, 2);
		$log{$key} = $val;
	}

	# 本文のキーを展開
	my ($bef, $mbody, $log, $flg, @ext);
	foreach (@$key) {

		# 本文に含めない部分を排除
		next if ($_ eq "mode");
		next if ($_ eq "need");
		next if ($_ eq "match");
		next if ($$in{match} && $_ eq $match2);
		next if ($bef eq $_);

		# 添付
		my $upl;
		if (/^clip-(\d+)$/i) {
			my $no = $1;
			if ($$in{"clip-$no"}) { push(@ext,$no); }

			# ログ蓄積
			my ($upl_file) = (split(/:/, $$in{"clip-$no"}))[0];
			$log .= "$_=$upl_file<>";
			my $tmp = "添付$no = $upl_file\n";
			Jcode::convert(\$tmp, 'jis', 'sjis');
			$mbody .= $tmp;

			# 内容を二重送信チェック
			if ($upl_file ne $log{$_}) {
				$flg++;
			}
			next;
		}

		# name値の名前
		my $key_name;
		if ($cf{replace}->{$_}) {
			$key_name = $cf{replace}->{$_};
		} else {
			$key_name = $_;
		}

		# 内容を二重送信チェック
		if ($$in{$_} ne $log{$key_name}) {
			$flg++;
		}

		# エスケープ
#		$$in{$_} =~ s/\0/ /g;
		$$in{$_} =~ s/\.\n/\. \n/g;

		# 添付ファイル風の文字列拒否
		$$in{$_} =~ s/Content-Disposition:\s*attachment;.*//ig;
		$$in{$_} =~ s/Content-Transfer-Encoding:.*//ig;
		$$in{$_} =~ s/Content-Type:\s*multipart\/mixed;\s*boundary=.*//ig;

		# ログ蓄積
		$log .= "$key_name=$$in{$_}<>";

		# 改行復元
		$$in{$_} =~ s/\t/\n/g;

		# HTMLタグ変換
		$$in{$_} =~ s/&lt;/</g;
		$$in{$_} =~ s/&gt;/>/g;
		$$in{$_} =~ s/&quot;/"/g;
		$$in{$_} =~ s/&#39;/'/g;
		$$in{$_} =~ s/&amp;/&/g;

		# 本文内容
		my $tmp;
		if ($$in{$_} =~ /\n/) {
			$tmp = "$key_name = \n$$in{$_}\n";
		} else {
			$tmp = "$key_name = $$in{$_}\n";
		}
		Jcode::convert(\$tmp, 'jis', 'sjis');
		$mbody .= $tmp;

		$bef = $_;
	}

	if (!$flg) {
		close(DAT);
		&error("二重送信のため処理を中止しました");
	}

	# ログ保存
	my @log;
	if ($cf{keep_log} > 0) {
		my $i = 0;
		seek(DAT, 0, 0);
		while(<DAT>) {
			push(@log,$_);

			$i++;
			last if ($i >= $cf{keep_log} - 1);
		}
	}
	seek(DAT, 0, 0);
	print DAT "date=$date1<>ip=$addr<>$log\n";
	print DAT @log if (@log > 0);
	truncate(DAT, tell(DAT));
	close(DAT);

	# 本文テンプレ内の変数を置き換え
	$tbody =~ s/!message!/$mbody/;

	# 返信テンプレ内の変数を置き換え
	$resbody =~ s/!message!/$mbody/ if ($cf{auto_res});

	# メールアドレスがない場合は送信先に置き換え
	my $email;
	if ($$in{email} eq "") {
		$email = $cf{mailto};
	} else {
		$email = $$in{email};
	}

	# MIMEエンコード
	my $sub_me = Jcode->new($cf{subject})->mime_encode;
	my $from;
	if ($$in{name}) {
		$$in{name} =~ s/[\r\n]//g;
		$from = Jcode->new("\"$$in{name}\" <$email>")->mime_encode;
	} else {
		$from = $email;
	}

	# 区切り線
	my $cut = "------_" . time . "_MULTIPART_MIXED_";

	# --- 送信内容フォーマット開始
	# ヘッダー
	my $body = "To: $cf{mailto}\n";
	$body .= "From: $from\n";
	$body .= "Subject: $sub_me\n";
	$body .= "MIME-Version: 1.0\n";
	$body .= "Date: $date2\n";

	# 添付ありのとき
	if (@ext > 0) {
		$body .= "Content-Type: multipart/mixed; boundary=\"$cut\"\n";
	} else {
		$body .= "Content-type: text/plain; charset=iso-2022-jp\n";
	}

	$body .= "Content-Transfer-Encoding: 7bit\n";
	$body .= "X-Mailer: $cf{version}\n\n";

	# 本文
	if (@ext > 0) {
		$body .= "--$cut\n";
		$body .= "Content-type: text/plain; charset=iso-2022-jp\n";
		$body .= "Content-Transfer-Encoding: 7bit\n\n";
	}
	$body .= "$tbody\n";

	# 返信内容フォーマット
	my $res_body;
	if ($cf{auto_res}) {
		$res_body .= "To: $email\n";
		$res_body .= "From: $cf{mailto}\n";
		$res_body .= "Subject: $sub_me\n";
		$res_body .= "MIME-Version: 1.0\n";
		$res_body .= "Content-type: text/plain; charset=iso-2022-jp\n";
		$res_body .= "Content-Transfer-Encoding: 7bit\n";
		$res_body .= "Date: $date2\n";
		$res_body .= "X-Mailer: $cf{version}\n\n";
		$res_body .= "$resbody\n";
	}

	# 添付あり
	if (@ext > 0) {
		foreach my $i (@ext) {

			# ファイル名と一時ファイル名に分割
			my ($fname, $tmpfile) = split(/:/, $$in{"clip-$i"}, 2);

			# ファイル名汚染チェック
			next if ($tmpfile !~ /^\d+\-$i\.\w+$/);

			# 一時ファイル名が存在しないときはスキップ
			next if (! -f "$cf{upldir}/$tmpfile");

			$fname = Jcode->new($fname)->mime_encode;

			# 添付ファイルを定義
			$body .= qq|--$cut\n|;
			$body .= qq|Content-Type: application/octet-stream; name="$fname"\n|;
			$body .= qq|Content-Disposition: attachment; filename="$fname"\n|;
			$body .= qq|Content-Transfer-Encoding: Base64\n\n|;

			# 一時ファイルをBase64変換
			my $buf;
			open(IN,"$cf{upldir}/$tmpfile");
			binmode(IN);
			while ( read(IN, $buf, 60*57) ) {
				$body .= encode_base64($buf);
			}
			close(IN);

			# 一時ファイル削除
			unlink("$cf{upldir}/$tmpfile");
		}
		$body .= "--$cut--\n";
	}

	# senmdailコマンド
	my $scmd = $cf{sendmail};
	if ($cf{send_fcmd}) {
		$scmd .= " -f $from";
	}

	# 本文送信
	open(MAIL,"| $scmd -t -i") or &error("メール送信失敗");
	print MAIL "$body\n";
	close(MAIL);

	# 返信送信
	if ($cf{auto_res}) {
		my $scmd = $cf{sendmail};
		if ($cf{send_fcmd}) {
			$scmd .= " -f $cf{mailto}";
		}
		open(MAIL,"| $scmd -t -i") or &error("メール送信失敗");
		print MAIL "$res_body\n";
		close(MAIL);
	}

	# リロード
	if ($cf{reload}) {
		if ($ENV{PERLXS} eq "PerlIS") {
			print "HTTP/1.0 302 Temporary Redirection\r\n";
			print "Content-type: text/html\n";
		}
		print "Location: $cf{back}\n\n";
		exit;

	# 完了メッセージ
	} else {
		open(IN,"$cf{tmpldir}/thx.html") or &error("open err: thx.html");
		my $tmpl = join('', <IN>);
		close(IN);

		# 表示
		print "Content-type: text/html\n\n";
		$tmpl =~ s/!back!/$cf{back}/g;
		&footer($tmpl);
	}
}

#-----------------------------------------------------------
#  フォームデコード
#-----------------------------------------------------------
sub parse_form {
	my ($clip,@key,@need,%in);
	foreach my $key ( $cgi->param() ) {
		my $val;

		# 添付
		if ($key =~ /^clip-\d+$/) {
			$val = $cgi->param($key);
			if ($val) { $clip++; }

		# テキスト系
		} else {

			# 複数値の場合はスペースで区切る
			$val = join(" ", $cgi->param($key));

			# 無害化/改行変換
			$key =~ s/[<>&"'\r\n]//g;
			$val =~ s/&/&amp;/g;
			$val =~ s/</&lt;/g;
			$val =~ s/>/&gt;/g;
			$val =~ s/"/&quot;/g;
			$val =~ s/'/&#39;/g;
			$val =~ s/\r\n/\t/g;
			$val =~ s/\r/\t/g;
			$val =~ s/\n/\t/g;

			# 文字コード変換
			if ($cf{conv_code}) {
				$key = $j->set($key)->sjis;
				$val = $j->set($val)->sjis;
			}

			# 入力必須
			if ($key =~ /^_(.+)/) {
				$key = $1;
				push(@need,$key);
			}
		}

		# 受け取るキーの順番を覚えておく
		push(@key,$key);

		# %inハッシュに代入
		$in{$key} = $val;
	}

	# post送信チェック
	if ($cf{postonly} && $ENV{REQUEST_METHOD} ne 'POST') {
		&error("不正なアクセスです");
	}
	# 添付拒否の場合
	if (!$cf{attach} && $clip) {
		&error("不正なアクセスです");
	}

	# リファレンスで返す
	return (\@key,\@need,\%in);
}

#-----------------------------------------------------------
#  入力エラー表示
#-----------------------------------------------------------
sub err_check {
	my $match2 = shift;

	# テンプレート読み込み
	my ($err,$flg,$cell,%fname,%err);
	open(IN,"$cf{tmpldir}/err2.html") or &error("open err: err2.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# テンプレート分割
	my ($head, $loop, $foot);
	if ($tmpl =~ /(.+)<!-- cell_begin -->(.+)<!-- cell_end -->(.+)/s) {
		($head, $loop, $foot) = ($1, $2, $3);
	} else {
		&error("テンプレートが不正です");
	}

	# 画面展開
	print "Content-type: text/html\n\n";
	print $head;
	my $bef;
	foreach my $key (@$key) {
		next if ($key eq "need");
		next if ($key eq "match");
		next if ($$in{match} && $key eq $match2);
		next if ($_ eq "match");
		next if ($bef eq $key);
		next if ($key eq "x");
		next if ($key eq "y");

		my $key_name = $key;
		my $tmp = $loop;
		if ($key =~ /^clip-(\d+)$/i) {
			$key_name = "添付$1";
		} elsif(defined($cf{replace}->{$key})) {
			$key_name = $cf{replace}->{$key};
		}
		$tmp =~ s/!key!/$key_name/;

		my $erflg;
		foreach my $err (@err) {
			if ($err eq $key) {
				$erflg++;
				last;
			}
		}
		# 入力なし
		if ($erflg) {
			$tmp =~ s/!val!/<span class="msg">$key_nameは入力必須です.<\/span>/;

		# 正常
		} else {

			# 添付のとき
			if ($key =~ /^clip-\d+$/i) {
				$tmp =~ s/!val!/$fname{$1}/;

			# テキスト（添付以外）
			} else {
				$$in{$key} =~ s/\t/<br \/>/g;
#				$$in{$key} =~ s/\0/ /g;
				$tmp =~ s/!val!/$$in{$key}/;
			}
		}
		print $tmp;

		$bef = $key;
	}
	print $foot;
	exit;
}

#-----------------------------------------------------------
#  エラー処理
#-----------------------------------------------------------
sub error {
	my $err = shift;

	open(IN,"$cf{tmpldir}/err1.html") or &error("open err: err1.html");
	print "Content-type: text/html\n\n";
	while (<IN>) {
		s/!error!/$err/;

		print;
	}
	close(IN);

	exit;
}

#-----------------------------------------------------------
#  フッター
#-----------------------------------------------------------
sub footer {
	my $foot = shift;

	# 著作権表記（削除・改変禁止）
	my $copy = <<EOM;
<p style="margin-top:2em;text-align:center;font-family:Verdana,Helvetica,Arial;font-size:10px;">
- <a href="http://www.kent-web.com/" target="_top">CLIP MAIL</a> -
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

#-----------------------------------------------------------
#  一時ディレクトリ掃除
#-----------------------------------------------------------
sub clean_dir {
	# 一時ディレクトリ内読み取り
	opendir(DIR,"$cf{upldir}");
	my @dir = readdir(DIR);
	closedir(DIR);

	foreach (@dir) {
		# 対象外はスキップ
		next if ($_ eq '.');
		next if ($_ eq '..');
		next if ($_ eq 'index.html');
		next if ($_ eq '.htaccess');

		# ファイル時間取得
		my $mtime = (stat("$cf{upldir}/$_"))[9];

		# 1時間以上経過しているファイルは削除
		if (time - $mtime > 3600) {
			unlink("$cf{upldir}/$_");
		}
	}
}

#-----------------------------------------------------------
#  時間取得
#-----------------------------------------------------------
sub get_time {
	$ENV{TZ} = "JST-9";
	my ($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime(time);
	my @week  = qw|Sun Mon Tue Wed Thu Fri Sat|;
	my @month = qw|Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec|;

	# 日時のフォーマット
	my $date1 = sprintf("%04d/%02d/%02d(%s) %02d:%02d:%02d",
			$year+1900,$mon+1,$mday,$week[$wday],$hour,$min,$sec);
	my $date2 = sprintf("%s, %02d %s %04d %02d:%02d:%02d",
			$week[$wday],$mday,$month[$mon],$year+1900,$hour,$min,$sec) . " +0900";

	return ($date1,$date2);
}

#-----------------------------------------------------------
#  ホスト名取得
#-----------------------------------------------------------
sub get_host {
	# ホスト名取得
	my $h = $ENV{REMOTE_HOST};
	my $a = $ENV{REMOTE_ADDR};

	if ($cf{gethostbyaddr} && ($h eq "" || $h eq $a)) {
		$h = gethostbyaddr(pack("C4", split(/\./, $a)), 2);
	}
	if ($h eq "") { $h = $a; }

	# チェック
	if ($cf{denyhost}) {
		my $flg;
		foreach ( split(/\s+/, $cf{denyhost}) ) {
			s/\./\\\./g;
			s/\*/\.\*/g;

			if ($h =~ /$_/i) { $flg++; last; }
		}
		if ($flg) { &error("アクセスを許可されていません"); }
	}

	return ($h,$a);
}

#-----------------------------------------------------------
#  画像リサイズ
#-----------------------------------------------------------
sub resize {
	my ($path,$ext) = @_;

	# サイズ取得
	my ($w,$h);
	if ($ext =~ /^gif$/i) {
		($w,$h) = &g_size($path);

	} elsif ($ext =~ /^jpe?g$/i) {
		($w,$h) = &j_size($path);

	} elsif ($ext =~ /^png$/i) {
		($w,$h) = &p_size($path);

	} elsif ($ext =~ /^bmp$/i) {
		($w,$h) = &b_size($path);
	}

	# 調整
	if ($w > $cf{img_max_w} || $h > $cf{img_max_h}) {
		my $w2 = $cf{img_max_w} / $w;
		my $h2 = $cf{img_max_h} / $h;
		my $key;
		if ($w2 < $h2) {
			$key = $w2;
		} else {
			$key = $h2;
		}
		$w = int ($w * $key) || 1;
		$h = int ($h * $key) || 1;
	}
	($w,$h);
}

#-----------------------------------------------------------
#  JPEGサイズ認識
#-----------------------------------------------------------
sub j_size {
	my $image = shift;

	my ($w,$h,$t);
	open(IMG, "$image") or return (0,0);
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

	($w,$h);
}

#-----------------------------------------------------------
#  GIFサイズ認識
#-----------------------------------------------------------
sub g_size {
	my $image = shift;

	my $data;
	open(IMG,"$image") or return (0,0);
	binmode(IMG);
	sysread(IMG, $data, 10);
	close(IMG);

	if ($data =~ /^GIF/) { $data = substr($data, -4); }
	my $w = unpack("v", substr($data, 0, 2));
	my $h = unpack("v", substr($data, 2, 2));

	($w,$h);
}

#-----------------------------------------------------------
#  PNGサイズ認識
#-----------------------------------------------------------
sub p_size {
	my $image = shift;

	my $data;
	open(IMG, "$image") or return (0,0);
	binmode(IMG);
	read(IMG, $data, 24);
	close(IMG);

	my $w = unpack("N", substr($data, 16, 20));
	my $h = unpack("N", substr($data, 20, 24));

	($w,$h);
}

#-----------------------------------------------------------
#  BMPサイズ
#-----------------------------------------------------------
sub b_size {
	my $image = shift;

	my $data;
	open(IMG, "$image") or return (0,0);
	binmode(IMG);
	seek(IMG, 0, 0);
	read(IMG, $data, 6);
	seek(IMG, 12, 1);
	read(IMG, $data, 8);

	unpack("VV", $data);
}

