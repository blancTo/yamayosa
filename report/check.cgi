#!/usr/local/bin/perl

#��������������������������������������������������������������������
#�� �A�N�Z�X��̓V�X�e��
#�� Access Report : check.cgi - 2011/08/25
#�� Copyright (c) KentWeb
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���W���[���錾
use strict;

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

# ���O�t�@�C���̃`�F�b�N
if (-e $cf{logfile}) {
	print "<li>���O�t�@�C���̃p�X : OK\n";

	# �p�[�~�b�V����
	if (-r $cf{logfile} && -w $cf{logfile}) {
		print "<li>���O�t�@�C���̃p�[�~�b�V���� : OK\n";
	} else {
		print "<li>���O�t�@�C���̃p�[�~�b�V���� : NG\n";
	}
} else {
	print "<li>���O�t�@�C���̃p�X : NG\n";
}

print <<EOM;
</ul>
</body>
</html>
EOM
exit;


