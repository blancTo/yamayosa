#!/usr/local/bin/perl

#��������������������������������������������������������������������
#�� LimeCounter : check.cgi - 2011/09/28
#�� Copyright (c) KentWeb
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
EOM

# �C���f�b�N�X�t�@�C��
if (-f $cf{idxfile}) {
	print "<li>�C���f�b�N�X�t�@�C���p�X : OK\n";
	if (-r $cf{idxfile} && -w $cf{idxfile}) {
		print "<li>�C���f�b�N�X�t�@�C���p�[�~�b�V���� : OK\n";
	} else {
		print "<li>�C���f�b�N�X�t�@�C���p�[�~�b�V���� : NG\n";
	}
} else {
	print "<li>�C���f�b�N�X�t�@�C���p�X : NG\n";
}

# �e���v���[�g
if (-f $cf{list_tmpl}) {
	print "<li>�e���v���[�g�p�X : OK\n";
} else {
	print "<li>�e���v���[�g�p�X : NG\n";
}

# �f�[�^�f�B���N�g��
if (-d $cf{datadir}) {
	print "<li>�f�[�^�f�B���N�g���p�X�FOK\n";
	if (-r $cf{datadir} && -w $cf{datadir} && -x $cf{datadir}) {
		print "<li>�f�[�^�f�B���N�g���p�[�~�b�V�����FOK\n";
	} else {
		print "<li>�f�[�^�f�B���N�g���p�[�~�b�V���� : NG\n";
	}
} else {
	print "<li>�f�[�^�f�B���N�g���p�X : NG\n";
}


print <<EOM;
</ul>
</body>
</html>
EOM
exit;


