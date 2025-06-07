#!/usr/local/bin/perl

#��������������������������������������������������������������������
#�� TOPICS BOARD : topics.cgi - 2011/11/23
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

# ��������
if ($in{mode} eq 'find') { &find_log; }
if ($in{poptag}) { &poptag; }
&bbs_list;

#-----------------------------------------------------------
#  �L���\��
#-----------------------------------------------------------
sub bbs_list {
	# �y�[�W��
	my $pg = $in{pg} || 0;

	# �f�[�^�F��
	my ($i,@log);
	open(IN,"$cf{logfile}") or &error("open err: $cf{logfile}");
	while(<IN>) {
		$i++;
		next if ($i < $pg + 1);
		next if ($i > $pg + $cf{pg_max});

		push(@log,$_);
	}
	close(IN);

	# �J�z�{�^���쐬
	my $pg_btn = &make_pgbtn($i, $pg);

	# �e���v���[�g�ǂݍ���
	open(IN,"$cf{tmpldir}/bbs.html") or &error("open err: bbs.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# �e���v���[�g����
	my ($head,$loop,$foot);
	if ($tmpl =~ /(.+)<!-- loop_begin -->(.+)<!-- loop_end -->(.+)/s) {
		($head,$loop,$foot) = ($1,$2,$3);
	} else {
		&error("�e���v���[�g���s���ł�");
	}

	# �����u��
	foreach ($head,$foot) {
		s/!bbs_title!/$cf{bbs_title}/g;
		s/!([a-z]+_cgi)!/$cf{$1}/g;
		s/!page_btn!/$pg_btn/g;
		s/!homepage!/$cf{homepage}/g;
	}

	# �w�b�_�\��
	print "Content-type: text/html\n\n";
	print $head;

	# �L���W�J
	foreach (@log) {
		my ($no,$date,$sub,$com,$e1,$w1,$h1,$e2,$w2,$h2,$e3,$w3,$h3,$tag,$clip,$tube) = split(/<>/);
		if ($tag == 1) {
			$com = &tag($com);
		} elsif ($cf{autolink}) {
			$com = &autolink($com);
		}

		# YouTube
		my $att;
		if ($clip eq 't') {
			$att = &tag($tube) if ($tube);

		# �摜
		} else {
			if ($e1) {
				my ($w,$h) = &resize($w1,$h1);
				$att .= qq|<a href="$cf{imgurl}/$no-1$e1" target="_blank"><img src="$cf{imgurl}/$no-1$e1" width="$w" height="$h" class="img"></a>\n|;
			}
			if ($e2) {
				my ($w,$h) = &resize($w2,$h2);
				$att .= qq|<a href="$cf{imgurl}/$no-2$e2" target="_blank"><img src="$cf{imgurl}/$no-2$e2" width="$w" height="$h" class="img"></a>\n|;
			}
			if ($e3) {
				my ($w,$h) = &resize($w3,$h3);
				$att .= qq|<a href="$cf{imgurl}/$no-3$e3" target="_blank"><img src="$cf{imgurl}/$no-3$e3" width="$w" height="$h" class="img"></a>\n|;
			}
		}

		# �����u��
		my $tmp = $loop;
		$tmp =~ s/!date!/$date/g;
		$tmp =~ s/!subject!/$sub/g;
		$tmp =~ s/!comment!/$com/g;
		$tmp =~ s/<!-- clip -->/$att/g;
		print $tmp;
	}

	# �t�b�^�i���쌠�\�L�͍폜�E���ς��֎~�j
	my $copy = &copyright;
	if ($foot =~ /(.+)(<\/body[^>]*>.*)/si) {
		print "$1$copy$2\n";
	} else {
		print "$foot$copy\n";
		print "</body></html>\n";
	}
	exit;
}

#-----------------------------------------------------------
#  ���[�h����
#-----------------------------------------------------------
sub find_log {
	# ����
	$in{cond} =~ s/\D//g;

	# ���������v���_�E��
	my %op = (1 => 'AND', 0 => 'OR');
	my $op_cond;
	foreach (1,0) {
		if ($in{cond} eq $_) {
			$op_cond .= qq|<option value="$_" selected>$op{$_}\n|;
		} else {
			$op_cond .= qq|<option value="$_">$op{$_}\n|;
		}
	}

	# �������s
	Jcode::convert(\$in{word}, 'sjis');
	my @log = &search($in{word}, $in{cond}) if ($in{word} ne '');

	# �e���v���[�g
	open(IN,"$cf{tmpldir}/find.html") or &error("open err: find.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# ����
	$tmpl =~ /(.+)<!-- loop_begin -->(.+)<!-- loop_end -->(.+)/s;
	my ($head, $loop, $foot) = ($1, $2, $3);

	foreach ($head, $foot) {
		s/!bbs_cgi!/$cf{bbs_cgi}/g;
		s/<!-- op_cond -->/$op_cond/;
		s/!word!/$in{word}/;
	}

	# �w�b�_��
	print "Content-type: text/html\n\n";
	print $head;

	# ���[�v��
	foreach (@log) {
		my ($no,$date,$sub,$com,$e1,$w1,$h1,$e2,$w2,$h2,$e3,$w3,$h3,$tag,$clip,$tube) = split(/<>/);
		if ($tag == 1) {
			$com = &tag($com);
		} elsif ($cf{autolink}) {
			$com = &autolink($com);
		}

		# YouTube
		my $att;
		if ($clip eq 't') {
			if ($tube) {
				$att = qq|[<a href="$cf{bbs_cgi}?poptag=$no" target="pop" onclick="popup('!bbs_cgi!?poptag=$no')">�����^�O</a>]|;
			}

		# �摜
		} else {
			if ($e1) {
				$att .= qq|[<a href="$cf{imgurl}/$no-1$e1" target="_blank">�摜1</a>]\n|;
			}
			if ($e2) {
				$att .= qq|[<a href="$cf{imgurl}/$no-2$e2" target="_blank">�摜2</a>]\n|;
			}
			if ($e3) {
				$att .= qq|[<a href="$cf{imgurl}/$no-3$e3" target="_blank">�摜3</a>]\n|;
			}
		}
		if ($att) { $com .= "<p>$att</p>"; }

		my $tmp = $loop;
		$tmp =~ s/!sub!/$sub/g;
		$tmp =~ s/!date!/$date/g;
		$tmp =~ s/!comment!/$com/g;
		print $tmp;
	}

	# �t�b�^��
	if ($foot =~ /(.+)(<\/body[^>]*>.*)/si) {
		print "$1$cf{copyright}$2";
	} else {
		print "$foot$cf{copyright}";
		print "</body></html>\n";
	}
	exit;
}

#-----------------------------------------------------------
#  �������s
#-----------------------------------------------------------
sub search {
	my ($word,$cond) = @_;

	# �L�[���[�h��z��
	$word =~ s/�@/ /g;
	my @wd = split(/\s+/, $word);

	# ��������
	my @log;
	open(IN,"$cf{logfile}") or &error("open err: $cf{logfile}");
	while (<IN>) {
		my ($no,$date,$nam,$eml,$sub,$com,$url,$hos,$pw,$tim) = split(/<>/);

		my $flg;
		foreach my $wd (@wd) {
			if (index("$nam $eml $sub $com $url", $wd) >= 0) {
				$flg++;
				if ($cond == 0) { last; }
			} else {
				if ($cond == 1) { $flg = 0; last; }
			}
		}
		next if (!$flg);

		push(@log,$_);
	}
	close(IN);

	# ��������
	return @log;
}

#-----------------------------------------------------------
#  �|�b�v�A�b�v�����^�O
#-----------------------------------------------------------
sub poptag {
	$in{poptag} =~ s/\D//g;

	my $tube_tag;
	open(IN,"$cf{logfile}") or &error("open err: $cf{logfile}");
	while(<IN>) {
		my ($no,$date,$sub,$com,$e1,$w1,$h1,$e2,$w2,$h2,$e3,$w3,$h3,$tag,$clip,$tube) = split(/<>/);

		if ($in{poptag} == $no) {
			$tube_tag = $tube;
			last;
		}
	}
	close(IN);

	open(IN,"$cf{tmpldir}/poptag.html") or &error("open err: poptag.html");
	print "Content-type: text/html\n\n";
	while(<IN>) {
		s/!tag!/&tag($tube_tag)/eg;

		print;
	}
	close(IN);

	exit;
}

#-----------------------------------------------------------
#  �摜���T�C�Y
#-----------------------------------------------------------
sub resize {
	my ($w,$h) = @_;

	# �摜�\���k��
	if ($w > $cf{max_img_w} || $h > $cf{max_img_h}) {
		my $w2 = $cf{max_img_w} / $w;
		my $h2 = $cf{max_img_h} / $h;
		my $key;
		if ($w2 < $h2) { $key = $w2; } else { $key = $h2; }
		$w = int ($w * $key) || 1;
		$h = int ($h * $key) || 1;
	}
	return ($w,$h);
}

#-----------------------------------------------------------
#  �J�z�{�^���쐬
#-----------------------------------------------------------
sub make_pgbtn {
	my ($i,$pg) = @_;

	# �y�[�W�J�z��`
	my $next = $pg + $cf{pg_max};
	my $back = $pg - $cf{pg_max};

	# �y�[�W�J�z�{�^���쐬
	my $pg_btn;
	if ($back >= 0 || $next < $i) {
		$pg_btn .= "Page: ";

		my ($x, $y) = (1, 0);
		while ($i > 0) {
			if ($pg == $y) {
				$pg_btn .= qq(| <b>$x</b> );
			} else {
				$pg_btn .= qq(| <a href="$cf{bbs_cgi}?pg=$y">$x</a> );
			}
			$x++;
			$y += $cf{pg_max};
			$i -= $cf{pg_max};
		}
		$pg_btn .= "|";
	}
	return $pg_btn;
}

#-----------------------------------------------------------
#  ���쌠�\�L�i�폜�E���ς��ւ��j
#-----------------------------------------------------------
sub copyright {
	my $copy = <<EOM;
<p style="margin-top:3em;text-align:center;font-family:Verdana,Helvetica,Arial;font-size:10px;">
- <a href="http://www.kent-web.com/" target="_top">Topics Board</a> -
</p>
EOM
	return $copy;
}

#-----------------------------------------------------------
#  ���������N
#-----------------------------------------------------------
sub autolink {
	local($_) = shift;

	s|(s?https?://[\w-.!~*'();/?:\@&=+\$,%#]+)|<a href="$1" target="_blank">$1</a>|g;
	$_;
}

#-----------------------------------------------------------
#  �^�O����
#-----------------------------------------------------------
sub tag {
	local($_) = @_;

	s/&lt;/</g;
	s/&gt;/>/g;
	s/&amp;/&/g;
	s/&quot;/"/g;
	$_;
}

