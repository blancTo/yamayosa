#!/usr/local/bin/perl

#��������������������������������������������������������������������
#�� CLIP MAIL : check.cgi - 2011/10/29
#�� copyright (c) KentWeb
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���W���[���錾
use strict;
use CGI::Carp qw(fatalsToBrowser);

# �O���t�@�C����荞��
require './init.cgi';
my %cf = &init;

print <<EOM;
Content-type: text/html

<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=shift_jis">
<title>Check Mode</title>
</head>
<body>
<b>Check Mode: [ $cf{version} ]</b>
<ul>
<li>Perl�o�[�W���� : $]
EOM

# sendmail�`�F�b�N
print "<li>sendmail�p�X : ";
if (-e $cf{sendmail}) {
	print "OK\n";
} else {
	print "NG �� $cf{sendmail}\n";
}

# �e���v���[�g
my @tmpl = qw|conf.html err1.html err2.html thx.html mail.txt reply.txt|;
foreach (@tmpl) {
	print "<li>�e���v���[�g�p�X ( $_ ) : ";

	if (-f "$cf{tmpldir}/$_") {
		print "OK\n";
	} else {
		print "NG\n";
	}
}

# �ꎞ�f�B���N�g��
if (-d $cf{upldir}) {
	print "<li>�ꎞ�f�B���N�g���p�X : OK\n";

	if (-r $cf{upldir} && -w $cf{upldir} && -x $cf{upldir}) {
		print "<li>�ꎞ�f�B���N�g���p�[�~�b�V���� : OK\n";
	} else {
		print "<li>�ꎞ�f�B���N�g���p�[�~�b�V���� : NG\n";
	}

} else {
	print "<li>�ꎞ�f�B���N�g���p�X : NG\n";
}

# ���O�t�@�C��
if (-f $cf{logfile}) {
	print "<li>���O�t�@�C���p�X : OK\n";

	if (-r $cf{logfile} && -w $cf{logfile}) {
		print "<li>���O�t�@�C���p�[�~�b�V���� : OK\n";
	} else {
		print "<li>���O�t�@�C���p�[�~�b�V���� : NG\n";
	}
} else {
	print "<li>���O�t�@�C���p�X : NG\n";
}

print <<EOM;
</ul>
</body>
</html>
EOM
exit;


