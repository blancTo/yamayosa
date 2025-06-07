#!/usr/local/bin/perl

#��������������������������������������������������������������������
#�� TOPICS BOARD : admin.cgi - 2011/03/06
#�� Copyright (c) KentWeb
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���W���[���錾
use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib "./lib";
use CGI::Minimal;
use Jcode;

# �ݒ�t�@�C���F��
require "./init.cgi";
my %cf = &init;

# �f�[�^��
CGI::Minimal::max_read_size($cf{maxdata});
my $cgi = CGI::Minimal->new;
&error('�e�ʃI�[�o�[') if ($cgi->truncated);
my %in = &parse_form($cgi);

# �F��
&check_passwd;

# ��������
if ($in{data_new}) { &data_new; }
if ($in{data_men}) { &data_men; }

# ���j���[���
&menu_html;

#-----------------------------------------------------------
#  ���j���[���
#-----------------------------------------------------------
sub menu_html {
	&header("���j���[TOP");

	print <<EOM;
<div align="center">
<p>�I���{�^���������Ă��������B</p>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<table border="1" cellpadding="5" cellspacing="0" class="menu">
<tr>
	<th>�I��</th>
	<th width="280">�������j���[</th>
</tr><tr>
	<td><input type="submit" name="data_new" value="�I��"></td>
	<td>�V�K�L���쐬</td>
</tr><tr>
	<td><input type="submit" name="data_men" value="�I��"></td>
	<td>�L�������e�i���X�i�C���E�폜�j</td>
</tr><tr>
	<td><input type="button" value="�I��" onclick="javascript:window.location='$cf{bbs_cgi}'"></td>
	<td>�f���ֈړ�</td>
</tr><tr>
	<td><input type="button" value="�I��" onclick="javascript:window.location='$cf{admin_cgi}'"></td>
	<td>���O�A�E�g</td>
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
#  �V�K�L��
#-----------------------------------------------------------
sub data_new {
	# �V�K�쐬���s
	if ($in{job} eq 'new2') { &add_data; }

	# �ҏW��
	my ($no,$date,$sub,$com,$e1,$w1,$h1,$e2,$w2,$h2,$e3,$w3,$h3,$tag,$clip,$tube) = @_;

	# �^�O�w��
	my $checked;
	if ($tag == 1) {
		$com =~ s/<br>/<br>\n/ig;
		$checked = "checked";
	} else {
		$com =~ s/<br>/\n/ig;
		$checked = "";
	}
	# �Y�t
	my %chk;
	if ($clip eq 't') {
		$chk{y} = "checked";
		$chk{i} = "";
	} else {
		$chk{y} = "";
		$chk{i} = "checked";
	}

	# �p�����[�^��`
	my $job = $in{job} ? "edit2" : "new2";

	# �V�K���e���͔N�������擾
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

	# �t�H�[���\��
	&header("���e�t�H�[��", "js");
	&back_btn($md);
	print <<"EOM";
<span class="ttl">�����e�t�H�[��</span>
<hr class="ttl" size="1">
<ul>
<li>HTML�^�O��L���ɂ���ꍇ���s�͖����ƂȂ邽�߁A���s���镔���� &lt;br&gt; �ƋL�q���邱�ƁB
<li>�摜�܂���YouTube�^�O�i�j�R���擙���j��Y�t���邱�Ƃ��ł��܂��i�C�Ӂj�B
</ul>
<form action="$cf{admin_cgi}" method="post" enctype="multipart/form-data">
<input type="hidden" name="pass" value="$in{pass}">
$hidden
<input type="hidden" name="job" value="$job">
<input type="hidden" name="no" value="$no">
<table border="1" cellpadding="5" cellspacing="0" class="form">
<tr>
	<th>�N����</th>
	<td><input type="text" name="date" value="$date" size="40"></td>
</tr><tr>
	<th>����</th>
	<td><input type="text" name="sub" value="$sub" size="40"></td>
</tr><tr>
	<th>�{��</th>
	<td><input type="checkbox" name="tag" value="1" $checked>HTML�^�O�L�� (�A�����s�͖���)<br>
		<textarea name="comment" cols="50" rows="6">$com</textarea>
	</td>
</tr><tr>
	<th>�Y�t</th>
	<td>
		<input type="radio" name="clip" value="i" onclick="entryChange1();" $chk{i}>�摜
		<input type="radio" name="clip" value="t" onclick="entryChange1();" $chk{y}>YouTube
	</td>
</tr><tr id="ibox">
	<th>�摜</th>
	<td nowrap>
EOM

	my %e = (1 => $e1, 2 => $e2, 3 => $e3);
	foreach my $i (1 .. 3) {
		print qq|�摜$i : <input type="file" name="upfile$i" size="35">\n|;
		if ($e{$i}) {
			print qq|&nbsp;<input type="checkbox" name="del$i" value="1">�폜\n|;
			print qq|[<a href="$cf{imgurl}/$no-$i$e{$i}" target="_blank">�摜</a>]\n|;
		}
		print "<br>\n";
	}

	print <<EOM;
	</td>
</tr><tr id="ybox">
	<th>YouTube<br>�^�O</th>
	<td><textarea name="tube" cols="50" rows="4">$tube</textarea></td>
</tr>
</table>
<br>
<input type="submit" value="���M����">
</form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  �L�������e�i���X
#-----------------------------------------------------------
sub data_men {
	# �폜
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

	# �C���t�H�[��
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

		# �C�����
		&data_new(@log);

	# �C�����s
	} elsif ($in{job} eq "edit2" && $in{no}) {

		# ���̓`�F�b�N
		&input_check;
		$in{tube} =~ s/<br>//g;

		# �R�[�h�ϊ�
		Jcode::convert(\$in{sub}, 'sjis');
		Jcode::convert(\$in{comment}, 'sjis');

		# �摜�A�b�v
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

				# �摜�폜�̂Ƃ�
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
				# �摜���ցi�g���q���قȂ�ꍇ�j
				if ($e1n && $e1n ne $e1) { unlink("$cf{imgdir}/$no-1$e1"); }
				if ($e2n && $e2n ne $e2) { unlink("$cf{imgdir}/$no-2$e2"); }
				if ($e3n && $e3n ne $e3) { unlink("$cf{imgdir}/$no-3$e3"); }

				# �摜����
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

	# �\�[�g
	} elsif ($in{job} eq "sort") {

		my (@sort,@data);
		open(DAT,"+< $cf{logfile}") or &error("open err: $cf{logfile}");
		while (<DAT>) {
			my ($no,$date,$sub,$com,$e1,$w1,$h1,$e2,$w2,$h2,$e3,$w3,$h3,$tag,$clip,$tube) = split(/<>/);

			push(@sort,$in{"sort:$no"});
			push(@data,$_);
		}

		# �\�[�g
		@data = @data[sort {$sort[$a] <=> $sort[$b]} 0 .. $#sort];

		# �X�V
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);
	}

	&header("���j���[ &gt; �L�������e�i���X");
	&back_btn();
	print <<"EOM";
<span class="ttl">���L�������e�i���X</span>
<hr class="ttl" size="1">
<ul>
<li>������I�����đ��M�{�^���������Ă��������B
<li>���ёւ��́u�\\�[�g�v��I�����A���Ԃ̐�����ύX���đ��M�{�^���������Ă��������B
</ul>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="data_men" value="1">
�����F
<select name="job">
<option value="edit">�C��
<option value="sort">�\\�[�g
<option value="dele">�폜
</select>
<input type="submit" value="���M����">
<p>
<table border="1" cellpadding="2" cellspacing="0" class="menu">
<tr>
  <th nowrap>�I��</th>
  <th nowrap>����</th>
  <th nowrap>�^�C�g��</th>
  <th nowrap>���t</th>
  <th nowrap>�摜</th>
</tr>
EOM

	# ���O�W�J
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
#  �L���ǉ�
#-----------------------------------------------------------
sub add_data {
	# ���̓`�F�b�N
	&input_check;
	$in{tube} =~ s/<br>//g;

	# �R�[�h�ϊ�
	Jcode::convert(\$in{sub}, 'sjis');
	Jcode::convert(\$in{comment}, 'sjis');

	# �f�[�^�I�[�v��
	my ($num,@file);
	open(DAT,"+< $cf{logfile}") or &error("open err: $cf{logfile}");
	while (<DAT>) {
		my ($no) = (split(/<>/))[0];

		if ($num < $no) { $num = $no; }
		push(@file,$_);
	}

	# �̔�
	$num++;

	# �摜�A�b�v
	my ($e1,$w1,$h1,$e2,$w2,$h2,$e3,$w3,$h3);
	if ($in{upfile1} || $in{upfile2} || $in{upfile3}) {
		($e1,$w1,$h1,$e2,$w2,$h2,$e3,$w3,$h3) = &upload($num);
	}

	# �ő�L��������
	while ( $cf{max} - 1 <= @file ) {
		my $del = pop(@file);
		my ($no,$date,$sub,$com,$e1,$w1,$h1,$e2,$w2,$h2,$e3,$w3,$h3,$tag,$clip,$tube) = split(/<>/, $del);
		unlink("$cf{imgdir}/$no-1$e1") if ($e1);
		unlink("$cf{imgdir}/$no-2$e2") if ($e2);
		unlink("$cf{imgdir}/$no-3$e3") if ($e3);
	}

	# �X�V
	unshift(@file,"$num<>$in{date}<>$in{sub}<>$in{comment}<>$e1<>$w1<>$h1<>$e2<>$w2<>$h2<>$e3<>$w3<>$h3<>$in{tag}<>$in{clip}<>$in{tube}<>\n");
	seek(DAT, 0, 0);
	print DAT @file;
	truncate(DAT, tell(DAT));
	close(DAT);

	&message("�V�K�L����ǉ����܂���");
}

#-----------------------------------------------------------
#  �摜�A�b�v���[�h
#-----------------------------------------------------------
sub upload {
	my $no = shift;

	my @ret;
	foreach my $i (1 .. 3) {
		# �g���q�擾
		my $ext;
		if ($cgi->param_filename("upfile$i") =~ /(\.jpe?g|\.png|\.gif)$/i) {
			$ext = $1;
		} else {
			push(@ret,('','',''));
			next;
		}
		$ext =~ tr/A-Z/a-z/;
		if ($ext eq '.jpeg') { $ext = '.jpg'; }

		# �Y�t�t�@�C����`
		my $upfile = "$cf{imgdir}/$no-$i$ext";

		# �A�b�v���[�h��������
		open(UP,"+> $upfile") or &error("up err: $upfile");
		binmode(UP);
		print UP $in{"upfile$i"};
		close(UP);

		chmod(0666,$upfile);

		# �摜�T�C�Y�擾
		my ($w, $h);
		if ($ext eq ".jpg") { ($w,$h) = &j_size($upfile); }
		elsif ($ext eq ".gif") { ($w,$h) = &g_size($upfile); }
		elsif ($ext eq ".png") { ($w,$h) = &p_size($upfile); }

		push(@ret,($ext,$w,$h));
	}

	return @ret;
}

#-----------------------------------------------------------
#  JPEG�T�C�Y�F��
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
#  GIF�T�C�Y�F��
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
#  PNG�T�C�Y�F��
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
#  HTML�w�b�_�[
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
			//�t�H�[��
			document.getElementById('ibox').style.display = "";
			document.getElementById('ybox').style.display = "none";
		}else if(radio[1].checked) {
			//�t�H�[��
			document.getElementById('ibox').style.display = "none";
			document.getElementById('ybox').style.display = "";
		}
	}
	//�I�����[�h�����A�����[�h���ɑI����ێ�
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
#  �p�X���[�h�F��
#-----------------------------------------------------------
sub check_passwd {
	# �p�X���[�h�������͂̏ꍇ�͓��̓t�H�[�����
	if ($in{pass} eq "") {
		&enter_form;

	# �p�X���[�h�F��
	} elsif ($in{pass} ne $cf{password}) {
		&error("�F�؂ł��܂���");
	}
}

#-----------------------------------------------------------
#  �������
#-----------------------------------------------------------
sub enter_form {
	&header("�������");
	print <<EOM;
<div align="center">
<form action="$cf{admin_cgi}" method="post">
<table width="380" style="margin-top:50px">
<tr>
	<td height="40" align="center">
		<fieldset><legend>�Ǘ��p�X���[�h����</legend><br>
		<input type="password" name="pass" value="" size="20">
		<input type="submit" value=" �F�� "><br><br>
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
#  �G���[
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
<input type="button" value="�O��ʂɖ߂�" onclick="history.back()">
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  �������b�Z�[�W
#-----------------------------------------------------------
sub message {
	my $msg = shift;

	&header("����");
	print <<EOM;
<div align="center" style="margin-top:3em;">
<hr width="350">
<p class="msg">$msg</p>
<hr width="350">
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="submit" value="�Ǘ���ʂɖ߂�">
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  �߂�{�^��
#-----------------------------------------------------------
sub back_btn {
	my $mode = shift;

	print <<EOM;
<div align="right">
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
@{[ $mode ? qq|<input type="submit" name="$mode" value="&lt; �O���">| : "" ]}
<input type="submit" value="&lt; ���j���[">
</form>
</div>
EOM
}

#-----------------------------------------------------------
#  ���̓`�F�b�N
#-----------------------------------------------------------
sub input_check {
	my $err;
	if (!$in{date}) { $err .= "���t�������͂ł�<br>"; }
	if (!$in{sub}) { $err .= "�^�C�g���������͂ł�<br>"; }
	if (!$in{comment}) { $err .= "���b�Z�[�W�������͂ł�<br>"; }
	&error($err) if ($err);

	# �^�O����
	if ($in{tag} == 1) {
		$in{comment} =~ s/<br>//g;
	}
}

