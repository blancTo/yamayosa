#!/usr/local/bin/perl

#��������������������������������������������������������������������
#�� TOPICS BOARD : check.cgi - 2011/10/29
#�� Copyright (c) KentWeb
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���W���[���錾
use strict;
use CGI::Carp qw(fatalsToBrowser);

# �O���t�@�C���捞��
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

# ���O�t�@�C��
if (-e $cf{logfile}) {
	print "<li>���O�t�@�C���p�X : OK\n";
	if (-r $cf{logfile} && -w $cf{logfile}) {
		print "<li>���O�p�[�~�b�V���� : OK\n";
	} else {
		print "<li>���O�p�[�~�b�V���� : NG\n";
	}
} else {
	print "<li>���O�t�@�C���p�X : NG\n";
}

# �摜�f�B���N�g��
if (-d $cf{imgdir}) {
	print "<li>�A�b�v���[�h�f�B���N�g���p�X : OK\n";
	if (-r $cf{imgdir} && -w $cf{imgdir} && -x $cf{imgdir}) {
		print "<li>�A�b�v���[�h�f�B���N�g���̃p�[�~�b�V���� : OK\n";
	} else {
		print "<li>�A�b�v���[�h�f�B���N�g���̃p�[�~�b�V���� : NG\n";
	}
} else {
	print "<li>�A�b�v���[�h�f�B���N�g���p�X : NG\n";
}

# �e���v���[�g
my @tmpl = qw|bbs error find poptag|;
foreach (@tmpl) {
	if (-e "$cf{tmpldir}/$_.html") {
		print "<li>�e���v���[�g( $_.html ) : OK\n";
	} else {
		print "<li>�e���v���[�g( $_.html ) : NG\n";
	}
}

print <<EOM;
</ul>
</body>
</html>
EOM
exit;

