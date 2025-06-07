#!/usr/local/bin/perl

#��������������������������������������������������������������������
#�� LimeCounter : admin.cgi - 2011/09/28
#�� Copyright (c) KentWeb
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���W���[���錾
use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib "./lib";
use Jcode;

# �O���t�@�C����荞��
require './init.cgi';
my %cf = &init;

# �f�[�^��
my %in = &parse_form;

# �F��
&check_passwd;

# �Ǘ����[�h
&admin_mode;

#-----------------------------------------------------------
#  �Ǘ����[�h
#-----------------------------------------------------------
sub admin_mode {
	# �V�K���
	if ($in{job} eq "new") {

		&new_form;

	# �V�K���s
	} elsif ($in{job} eq "new2") {

		if ($in{file} eq "http://") { $in{file} = ""; }
		if ($in{link} eq "http://") { $in{link} = ""; }
		if ($in{id} =~ /\W/) { &error("ID�͉p�����Ŏw�肵�Ă�������"); }
		if ($in{id} eq "check") { &error("ID����check�͎g�p�ł��܂���"); }
		if ($in{sub} eq "") { &error("�^�C�g�����������͂ł�"); }
		if ($cf{type} >= 2 && $in{file} eq "") {
			&error("�_�E�����[�h�t�@�C���������͂ł�");
		}

		# �R�[�h�ϊ�
		Jcode::convert(\$in{sub}, 'sjis');

		# index�`�F�b�N
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

		# �d��
		if ($flg) {
			close(DAT);
			&error("$in{id}�͊�����ID�Əd�����Ă��܂�");
		}

		# index�X�V
		seek(DAT, 0, 0);
		print DAT "$in{id}<>$in{sub}<>$in{link}<>$in{file}<>\n";
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);

		# �J�E���^�l
		open(OUT,"+> $cf{datadir}/$in{id}.dat") || &error("write err: $in{id}.dat");
		print OUT "$in{count}::\n";
		close(OUT);

	# �폜
	} elsif ($in{id} && $in{job} eq "dele") {

		# index�}�b�`���O
		my @data;
		open(DAT,"+< $cf{idxfile}") || &error("Open Error: $cf{idxfile}");
		while (<DAT>) {
			my ($id) = split(/<>/);

			next if ($in{id} eq $id);

			push(@data,$_);
		}

		# index�X�V
		seek(DAT, 0, 0);
		print DAT @data;
		truncate(DAT, tell(DAT));
		close(DAT);

		# ���O�폜
		unlink("$cf{datadir}/$in{id}.dat");

	# �C�����
	} elsif ($in{id} && $in{job} eq "edit") {

		my ($id,$sub,$link,$file);

		# index�`�F�b�N
		open(IN,"$cf{idxfile}") || &error("Open Error: $cf{idxfile}");
		while (<IN>) {
			($id,$sub,$link,$file) = split(/<>/);

			if ($in{id} eq $id) { last; }
		}
		close(IN);

		&edit_form($id,$sub,$link,$file);

	# �C�����s
	} elsif ($in{id} && $in{job} eq "edit2") {

		if ($in{file} eq "http://") { $in{file} = ""; }
		if ($in{link} eq "http://") { $in{link} = ""; }
		if ($in{sub} eq "") { &error("�^�C�g�����������͂ł�"); }
		if ($cf{type} >= 2 && $in{file} eq "") {
			&error("�_�E�����[�h�t�@�C���������͂ł�");
		}

		# �R�[�h�ϊ�
		Jcode::convert(\$in{sub}, 'sjis');

		# index���ւ�
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

		# �J�E���^�X�V
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

	&header("�Ǘ����[�h");
	print <<EOM;
<form action="$cf{admin_cgi}">
<input type="submit" value="�����O�A�E�g">
</form>
<ul>
<li>������I�����đ��M�{�^���������Ă��������B
</ul>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
�����F <select name="job">
<option value="new">�V�K
<option value="edit">�C��
<option value="dele">�폜
</select>
<input type="submit" value="���M����">
<dl>
EOM

	# index�W�J
	open(IN,"$cf{idxfile}") || &error("open err: $cf{idxfile}");
	while (<IN>) {
		my ($id,$sub,$link,$file) = split(/<>/);

		# �J�E���^�ǂݎ��
		open(DB,"$cf{datadir}/$id.dat");
		my $count = <DB>;
		close(DB);

		my ($count,$ip) = split(/:/, $count);

		# ����؂�
		$count = &comma($count);

		print qq|<dt><hr><input type="radio" name="id" value="$id"><b>$id</b>\n|;
		print qq|<dd>[�^�C�g��] $sub &nbsp; [�J�E���^] $count\n|;

		print "<dd>[�����N��] <a href=\"$link\">$link</a>\n" if ($link);
		print "<dd>[�t�@�C��] <a href=\"$file\">$file</a>\n" if ($file);
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
#  �V�K���
#-----------------------------------------------------------
sub new_form {
	&header("�V�KID���s");
	print <<EOM;
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="submit" value="&lt; �O�ɖ߂�">
</form>
<ul>
<li>�V�K��ID���𔭍s���܂��B
<li>ID���͔C�ӂ̉p�����Ŏw�肵�Ă��������B�啶���Ə������͕ʕ��Ƃ��Ĉ����܂��B
</ul>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="mode" value="admin">
<input type="hidden" name="job" value="new2">
ID��<br>
<input type="text" name="id" value="" size="10"> �i�p�����Ŏw��j<br>
�^�C�g����<br>
<input type="text" name="sub" value="" size="30"><br>
�J�E���^�l<br>
<input type="text" name="count" value="0" size=10><br>
EOM

	if ($cf{type} >= 2) {
		print qq|�_�E�����[�h�t�@�C��<br>\n|;
		print qq|<input type="text" name="file" value="http://" size="50"><br>\n|;
	}

	print <<EOM;
���X�g�Ƀ����N����y�[�W�i�C�Ӂj<br>
<input type="text" name="link" value="http://" size="50">
<p>
<input type="submit" value="���M����"></form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  �ҏW���
#-----------------------------------------------------------
sub edit_form {
	my ($id,$sub,$link,$file) = @_;
	$link ||= 'http://';
	$file ||= 'http://';

	# �J�E���^�ǂݍ���
	open(DB,"$cf{datadir}/$in{id}.dat");
	my $data = <DB>;
	close(DB);

	# ����
	my ($count, $ip) = split(/:/, $data);

	# �t�H�[���\��
	&header("ID�ҏW");
	print <<"EOM";
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="submit" value="&lt; �O�ɖ߂�">
</form>
<ul>
<li><b>$id</b>�̕ҏW���s���܂��B
<li>�C�����镔���̂ݕύX�����M�{�^���������Ă��������B
</ul>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="mode" value="admin">
<input type="hidden" name="job" value="edit2">
<input type="hidden" name="cnt" value="$count">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="id" value="$in{id}">
�^�C�g����<br>
<input type="text" name="sub" value="$sub" size="30"><br>
�J�E���^�l<br>
<input type="text" name="count" value="$count" size="10"><br>
EOM

	if ($cf{type} >= 2) {
		print "�_�E�����[�h�t�@�C��<br>\n";
		print "<input type=text name=file value=\"$file\" size=50><br>\n";
	}

	print <<EOM;
���X�g�Ƀ����N����y�[�W�i�C�Ӂj<br>
<input type="text" name="link" value="$link" size="50">
<p>
<input type="submit" value="���M����"></form>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  �t�H�[���f�R�[�h
#-----------------------------------------------------------
sub parse_form {
	my ($buf,%in);
	if ($ENV{REQUEST_METHOD} eq "POST") {
		&error('�󗝂ł��܂���') if ($ENV{CONTENT_LENGTH} > $cf{maxdata});
		read(STDIN, $buf, $ENV{CONTENT_LENGTH});
	} else {
		$buf = $ENV{QUERY_STRING};
	}
	foreach ( split(/&/, $buf) ) {
		my ($key,$val) = split(/=/);
		$val =~ tr/+/ /;
		$val =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("H2", $1)/eg;

		# ������
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
#  HTML�w�b�_�[
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
#  �G���[����
#-----------------------------------------------------------
sub error {
	my $err =shift;

	&header("ERROR!");
	print <<EOM;
<div align="center">
<h3>ERROR !</h3>
<p><font color="#dd0000">$err</font></p>
<form>
<input type="button" value="�O��ʂɖ߂�" onclick="history.back()">
</form>
</div>
</body>
</html>
EOM
	exit;
}
