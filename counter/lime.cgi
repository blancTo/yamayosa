#!/usr/local/bin/perl

#��������������������������������������������������������������������
#�� LimeCounter : lime.cgi - 2011/07/14
#�� Copyright (c) KentWeb
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���W���[���錾
use strict;

# �O���t�@�C����荞��
require './init.cgi';
my %cf = &init;

# �O���f�[�^�󂯎��
my $buf = $ENV{QUERY_STRING};
$buf =~ s/\W//g;
&error("ID���s��") if ($buf eq '');

# �f�[�^�t�@�C����`
my $datafile = "$cf{datadir}/$buf.dat";

# �J�E���g�A�b�v
&count_up;

#-----------------------------------------------------------
#  �J�E���g����
#-----------------------------------------------------------
sub count_up {
	# IP�A�h���X�擾
	my $addr = $ENV{REMOTE_ADDR};

	# �f�[�^�ǂݎ��
	open(DAT,"+< $datafile") || &error("open errr: $datafile");
	eval "flock(DAT, 2);";
	my $data = <DAT>;

	# �f�[�^����
	my ($count, $ip) = split(/:/, $data);

	# �J�E���g�A�b�v
	if (!$cf{ip_chk} || ($cf{ip_chk} && $addr ne $ip)) {
		$count++;

		seek(DAT, 0, 0);
		print DAT "$count:$addr";
		truncate(DAT, tell(DAT));
	}
	close(DAT);

	# �y�[�W�J�E���^�̂Ƃ�
	if ($cf{type} == 1) {

		# �_�~�[�摜
		my @gif = qw(
			47 49 46 38 39 61 02 00 02 00 80 00	00 00 00 00 ff ff ff
			21 f9 04 01 00 00 01 00 2c 00 00 00 00 02 00 02 00 00 02
			02 8c 53 00 3b
		);

		# �_�~�[�摜�\��
		print "Content-type: image/gif\n\n";
		foreach (@gif) {
			print pack('C*',hex($_));
		}
		exit;

	# �_�E�����[�h�J�E���^�̂Ƃ�
	} else {

		# index�ǂݎ��
		my ($flg, $jump);
		open(IN,"$cf{idxfile}") || &error("open err: $cf{idxfile}");
		while (<IN>) {
			my ($id,$sub,$link,$file) = split(/<>/);

			if ($buf eq $id) {
				$flg++;
				$jump = $file;
				last;
			}
		}
		close(IN);

		if (!$flg) { &error("ID���s���ł�"); }

		# Location�w�b�_
		if ($cf{type} == 2) {

			# PerlIS�Ή�
			if ($ENV{PERLXS} eq "PerlIS") {
				print "HTTP/1.0 302 Temporary Redirection\r\n";
 				print "Content-type: text/html\n";
			}

			# �t�@�C���ֈړ�
			print "Location: $jump\n\n";
			exit;

		# meta�^�O
		} else {
			&header("<meta http-equiv=\"refresh\" content=\"1; url=$jump\">");
			print qq|<div align="center">\n|;
			print qq|<p>�_�E�����[�h�ł��Ȃ��ꍇ��<a href="$jump">����</a>���N���b�N�B</p>\n|;
			print qq|</div>\n|;
			print qq|</body></html>\n|;
			exit;
		}
	}
}

#-----------------------------------------------------------
#  �G���[����
#-----------------------------------------------------------
sub error {
	my $err = shift;

	# �_�E�����[�h�J�E���^�̏ꍇ
	if ($cf{type} > 1) {
		&header();
		print "<h3>ERROR</h3>\n";
		print "<p>$err</p>\n";
		print "</body></html>\n";
		exit;

	# �y�[�W�J�E���^�̏ꍇ
	} else {
		die "error: $err";
	}
}

#-----------------------------------------------------------
#  HTML�w�b�_
#-----------------------------------------------------------
sub header {
	my ($meta) = @_;

	print "Content-type: text/html\n\n";
	print <<EOM;
<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=shift_jis">
$meta
<title>$cf{version}</title>
</head>
<body>
EOM
}

