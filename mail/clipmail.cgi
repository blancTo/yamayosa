#!/usr/local/bin/perl

#��������������������������������������������������������������������
#�� CLIP MAIL : clipmail.cgi - 2011/11/10
#�� copyright (c) KentWeb
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���W���[�����s
use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib './lib';
use CGI::Minimal;
use Jcode;
use MIME::Base64;

# Jcode�錾
my $j = new Jcode;

# �O���t�@�C����荞��
require './init.cgi';
my %cf = &init;

# �f�[�^��
CGI::Minimal::max_read_size($cf{maxdata});
my $cgi = CGI::Minimal->new;
&error('�e�ʃI�[�o�[') if ($cgi->truncated);
my ($key,$need,$in) = &parse_form;

# �֎~���[�h�`�F�b�N
if ($cf{no_wd}) {
	my $flg;
	foreach (@$key) {
		foreach my $wd ( split(/,/, $cf{no_wd}) ) {
			if (index($$in{$_},$wd) >= 0) {
				$flg++;
				last;
			}
		}
		if ($flg) { &error("�֎~���[�h���܂܂�Ă��܂�"); }
	}
}

# �z�X�g�擾���`�F�b�N
my ($host,$addr) = &get_host;

# �K�{���̓`�F�b�N
my ($check,@err,@need);
if ($$in{need} || @$need > 0) {

	# �A���_�[�o�[�ɂ��K�{�w��
	if (@$need > 0) {
		@need = @$need;
	}

	# need�t�B�[���h�̒l��K�{�z��ɉ�����
	my @tmp = split(/\s+/, $$in{need});
	push(@need,@tmp);

	# �K�{�z��̏d���v�f��r������
	my (@uniq,%seen);
	foreach (@need) {
		push(@uniq,$_) unless $seen{$_}++;
	}

	# �K�{���ڂ̓��͒l���`�F�b�N����
	foreach (@uniq) {

		# �t�B�[���h�̒l���������Ă��Ȃ����́i���W�I�{�^�����j
		if (!defined($$in{$_})) {
			$check++;
			push(@$key,$_);
			push(@err,$_);

		# ���͂Ȃ��̏ꍇ
		} elsif ($$in{$_} eq "") {
			$check++;
			push(@err,$_);
		}
	}
}

# ���͓��e�}�b�`
my ($match1,$match2);
if ($$in{match}) {
	($match1,$match2) = split(/\s+/, $$in{match}, 2);

	if ($$in{$match1} ne $$in{$match2}) {
		&error("$match1��$match2�̍ē��͓��e���قȂ�܂�");
	}
}

# ���̓`�F�b�N�m�F���
if ($check) {
	&err_check($match2);
}

# E-mail�����`�F�b�N
if ($$in{email} =~ /\,/) {
	&error("���[���A�h���X�ɃR���} ( , ) ���܂܂�Ă��܂�");
}
if ($$in{email} ne '' && $$in{email} !~ /^[\w\.\-]+\@[\w\.\-]+\.[a-zA-Z]{2,}$/) {
	&error("���[���A�h���X�̏������s���ł�");
}

# �v���r���[
if ($$in{mode} ne "send") {
	&preview;

# ���M���s
} else {
	&send_mail;
}

#-----------------------------------------------------------
#  �v���r���[
#-----------------------------------------------------------
sub preview {
	# ���M���e�`�F�b�N
	&error("�f�[�^���擾�ł��܂���") if (@$key == 0);

	# ���Ԏ擾
	my $time = time;

	# ���g���q���n�b�V����
	my %ex;
	foreach ( split(/,/, $cf{extension}) ) {
		$ex{$_}++;
	}

	# �Y�t�m�F
	my ($err,@ext,%file,%ext);
	foreach (@$key) {
		if (/^clip-(\d+)$/) {
			my $num = $1;

			# �t�@�C����
			my $fname = $j->set($cgi->param_filename("clip-$1"))->euc;
			if ($fname =~ /([^\\\/:]+)\.([^\\\/:\.]+)$/) {

				# �t�@�C����
				$file{$num} = "$1.$2";
				$file{$num} = $j->set($file{$num},'euc')->sjis;

				# �g���q�`�F�b�N
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
		&error("�Y�t�t�@�C���ŋ�����Ȃ��g���q������܂� �� $err");
	}

	# �Y�t����
	if (@ext > 0) {

		# �ꎞ�f�B���N�g����|��
		&clean_dir;

		# �A�b�v���[�h���s
		foreach my $i (@ext) {

			# �t�@�C����`
			my $upfile = "$cf{upldir}/$time-$i.$ext{$i}";

			# �t�@�C����������
			my $buf;
			open(UP,"+> $upfile") or &error("up err: $upfile");
			binmode(UP);
			print UP $$in{"clip-$i"};
			close(UP);
		}
	}

	# ��ʓW�J
	open(IN,"$cf{tmpldir}/conf.html") or &error("open err: conf.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# �e���v���[�g����
	my ($head,$loop,$foot);
	if ($tmpl =~ /(.+)<!-- cell_begin -->(.+)<!-- cell_end -->(.+)/s) {
		($head,$loop,$foot) = ($1,$2,$3);
	} else {
		&error("�e���v���[�g���s���ł�");
	}

	# ����
	my $hidden .= qq|<input type="hidden" name="mode" value="send" />\n|;

	# ����
	my ($bef,$item);
	foreach my $key (@$key) {
		next if ($bef eq $key);

		# �摜SUBMIT�{�^���͖���
		next if ($key eq "x");
		next if ($key eq "y");
		if ($key eq "need" || $key eq "match" || ($$in{match} && $key eq $match2)) {
			next;
		}

		# �Y�t�̂Ƃ�
		if ($key =~ /^clip-(\d+)$/i) {

			my $no = $1;
			if (defined($file{$no})) {
				$hidden .= qq|<input type="hidden" name="$key" value="$file{$no}:$time-$no.$ext{$no}" />\n|;
			} else {
				$hidden .= qq|<input type="hidden" name="$key" value="" />\n|;
			}

			my $tmp = $loop;
			$tmp =~ s/!key!/�Y�t$no/;

			# �摜�̂Ƃ�
			if ($ext{$no} =~ /^(gif|jpe?g|png|bmp)$/i && -B "$cf{upldir}/$time-$no.$ext{$no}") {

				# �\���T�C�Y����
				my ($w,$h) = &resize("$cf{upldir}/$time-$no.$ext{$no}", $1);
				$tmp =~ s|!val!|<img src="$cf{uplurl}/$time-$no.$ext{$no}" width="$w" height="$h" alt="$file{$no}" />|;

			# �摜�ȊO
			} else {
				$tmp =~ s/!val!/$file{$no}/;
			}
			$item .= $tmp;

		# �e�L�X�g�i�Y�t�ȊO�j
		} else {

#			$$in{$key} =~ s/\0/ /g;
			$hidden .= qq|<input type="hidden" name="$key" value="$$in{$key}" />\n|;

			# ���s�ϊ�
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

	# �����u��
	for ( $head, $foot ) {
		s/!mail_cgi!/$cf{mail_cgi}/g;
		s/<!-- hidden -->/$hidden/g;
	}

	# ��ʓW�J
	print "Content-type: text/html\n\n";
	print $head, $item;

	# �t�b�^
	&footer($foot);
}

#-----------------------------------------------------------
#  ���M���s
#-----------------------------------------------------------
sub send_mail {
	# ���M���e�`�F�b�N
	&error("�f�[�^���擾�ł��܂���") if (@$key == 0);

	# ���Ԏ擾
	my ($date1, $date2) = &get_time;

	# �u���E�U���
	my $agent = $ENV{HTTP_USER_AGENT};
	$agent =~ s/[<>&"'()+;]//g;

	# �{���e���v���ǂݍ���
	my $tbody;
	open(IN,"$cf{tmpldir}/mail.txt") or &error("open err: mail.txt");
	my $tbody = join('', <IN>);
	close(IN);

	# ���s
	$tbody =~ s/\r\n/\n/g;
	$tbody =~ s/\r/\n/g;

	# �e���v���ϐ��ϊ�
	$tbody =~ s/!date!/$date1/g;
	$tbody =~ s/!agent!/$agent/g;
	$tbody =~ s/!host!/$host/g;
	Jcode::convert(\$tbody, 'jis', 'sjis');

	# �����ԐM����̂Ƃ�
	my $resbody;
	if ($cf{auto_res}) {

		# �e���v��
		open(IN,"$cf{tmpldir}/reply.txt") or &error("open err: reply.txt");
		$resbody = join('', <IN>);
		close(IN);

		# ���s
		$resbody =~ s/\r\n/\n/g;
		$resbody =~ s/\r/\n/g;

		# �ϐ��ϊ�
		$resbody =~ s/!date!/$date1/g;
		Jcode::convert(\$resbody, 'jis', 'sjis');
	}

	# ���O�t�@�C���I�[�v��
	open(DAT,"+< $cf{logfile}") or &error("open err: $cf{logfile}");
	eval "flock(DAT, 2);";

	# �擪�s�𕪉�
	my $top_log = <DAT>;
	my ($log_date, $log_ip, $log_data) = split(/<>/, $top_log, 3);

	# �n�b�V��%log�Ɋe���ڂ���
	my %log;
	foreach ( split(/<>/, $log_data) ) {
		my ($key,$val) = split(/=/, $_, 2);
		$log{$key} = $val;
	}

	# �{���̃L�[��W�J
	my ($bef, $mbody, $log, $flg, @ext);
	foreach (@$key) {

		# �{���Ɋ܂߂Ȃ�������r��
		next if ($_ eq "mode");
		next if ($_ eq "need");
		next if ($_ eq "match");
		next if ($$in{match} && $_ eq $match2);
		next if ($bef eq $_);

		# �Y�t
		my $upl;
		if (/^clip-(\d+)$/i) {
			my $no = $1;
			if ($$in{"clip-$no"}) { push(@ext,$no); }

			# ���O�~��
			my ($upl_file) = (split(/:/, $$in{"clip-$no"}))[0];
			$log .= "$_=$upl_file<>";
			my $tmp = "�Y�t$no = $upl_file\n";
			Jcode::convert(\$tmp, 'jis', 'sjis');
			$mbody .= $tmp;

			# ���e���d���M�`�F�b�N
			if ($upl_file ne $log{$_}) {
				$flg++;
			}
			next;
		}

		# name�l�̖��O
		my $key_name;
		if ($cf{replace}->{$_}) {
			$key_name = $cf{replace}->{$_};
		} else {
			$key_name = $_;
		}

		# ���e���d���M�`�F�b�N
		if ($$in{$_} ne $log{$key_name}) {
			$flg++;
		}

		# �G�X�P�[�v
#		$$in{$_} =~ s/\0/ /g;
		$$in{$_} =~ s/\.\n/\. \n/g;

		# �Y�t�t�@�C�����̕����񋑔�
		$$in{$_} =~ s/Content-Disposition:\s*attachment;.*//ig;
		$$in{$_} =~ s/Content-Transfer-Encoding:.*//ig;
		$$in{$_} =~ s/Content-Type:\s*multipart\/mixed;\s*boundary=.*//ig;

		# ���O�~��
		$log .= "$key_name=$$in{$_}<>";

		# ���s����
		$$in{$_} =~ s/\t/\n/g;

		# HTML�^�O�ϊ�
		$$in{$_} =~ s/&lt;/</g;
		$$in{$_} =~ s/&gt;/>/g;
		$$in{$_} =~ s/&quot;/"/g;
		$$in{$_} =~ s/&#39;/'/g;
		$$in{$_} =~ s/&amp;/&/g;

		# �{�����e
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
		&error("��d���M�̂��ߏ����𒆎~���܂���");
	}

	# ���O�ۑ�
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

	# �{���e���v�����̕ϐ���u������
	$tbody =~ s/!message!/$mbody/;

	# �ԐM�e���v�����̕ϐ���u������
	$resbody =~ s/!message!/$mbody/ if ($cf{auto_res});

	# ���[���A�h���X���Ȃ��ꍇ�͑��M��ɒu������
	my $email;
	if ($$in{email} eq "") {
		$email = $cf{mailto};
	} else {
		$email = $$in{email};
	}

	# MIME�G���R�[�h
	my $sub_me = Jcode->new($cf{subject})->mime_encode;
	my $from;
	if ($$in{name}) {
		$$in{name} =~ s/[\r\n]//g;
		$from = Jcode->new("\"$$in{name}\" <$email>")->mime_encode;
	} else {
		$from = $email;
	}

	# ��؂��
	my $cut = "------_" . time . "_MULTIPART_MIXED_";

	# --- ���M���e�t�H�[�}�b�g�J�n
	# �w�b�_�[
	my $body = "To: $cf{mailto}\n";
	$body .= "From: $from\n";
	$body .= "Subject: $sub_me\n";
	$body .= "MIME-Version: 1.0\n";
	$body .= "Date: $date2\n";

	# �Y�t����̂Ƃ�
	if (@ext > 0) {
		$body .= "Content-Type: multipart/mixed; boundary=\"$cut\"\n";
	} else {
		$body .= "Content-type: text/plain; charset=iso-2022-jp\n";
	}

	$body .= "Content-Transfer-Encoding: 7bit\n";
	$body .= "X-Mailer: $cf{version}\n\n";

	# �{��
	if (@ext > 0) {
		$body .= "--$cut\n";
		$body .= "Content-type: text/plain; charset=iso-2022-jp\n";
		$body .= "Content-Transfer-Encoding: 7bit\n\n";
	}
	$body .= "$tbody\n";

	# �ԐM���e�t�H�[�}�b�g
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

	# �Y�t����
	if (@ext > 0) {
		foreach my $i (@ext) {

			# �t�@�C�����ƈꎞ�t�@�C�����ɕ���
			my ($fname, $tmpfile) = split(/:/, $$in{"clip-$i"}, 2);

			# �t�@�C���������`�F�b�N
			next if ($tmpfile !~ /^\d+\-$i\.\w+$/);

			# �ꎞ�t�@�C���������݂��Ȃ��Ƃ��̓X�L�b�v
			next if (! -f "$cf{upldir}/$tmpfile");

			$fname = Jcode->new($fname)->mime_encode;

			# �Y�t�t�@�C�����`
			$body .= qq|--$cut\n|;
			$body .= qq|Content-Type: application/octet-stream; name="$fname"\n|;
			$body .= qq|Content-Disposition: attachment; filename="$fname"\n|;
			$body .= qq|Content-Transfer-Encoding: Base64\n\n|;

			# �ꎞ�t�@�C����Base64�ϊ�
			my $buf;
			open(IN,"$cf{upldir}/$tmpfile");
			binmode(IN);
			while ( read(IN, $buf, 60*57) ) {
				$body .= encode_base64($buf);
			}
			close(IN);

			# �ꎞ�t�@�C���폜
			unlink("$cf{upldir}/$tmpfile");
		}
		$body .= "--$cut--\n";
	}

	# senmdail�R�}���h
	my $scmd = $cf{sendmail};
	if ($cf{send_fcmd}) {
		$scmd .= " -f $from";
	}

	# �{�����M
	open(MAIL,"| $scmd -t -i") or &error("���[�����M���s");
	print MAIL "$body\n";
	close(MAIL);

	# �ԐM���M
	if ($cf{auto_res}) {
		my $scmd = $cf{sendmail};
		if ($cf{send_fcmd}) {
			$scmd .= " -f $cf{mailto}";
		}
		open(MAIL,"| $scmd -t -i") or &error("���[�����M���s");
		print MAIL "$res_body\n";
		close(MAIL);
	}

	# �����[�h
	if ($cf{reload}) {
		if ($ENV{PERLXS} eq "PerlIS") {
			print "HTTP/1.0 302 Temporary Redirection\r\n";
			print "Content-type: text/html\n";
		}
		print "Location: $cf{back}\n\n";
		exit;

	# �������b�Z�[�W
	} else {
		open(IN,"$cf{tmpldir}/thx.html") or &error("open err: thx.html");
		my $tmpl = join('', <IN>);
		close(IN);

		# �\��
		print "Content-type: text/html\n\n";
		$tmpl =~ s/!back!/$cf{back}/g;
		&footer($tmpl);
	}
}

#-----------------------------------------------------------
#  �t�H�[���f�R�[�h
#-----------------------------------------------------------
sub parse_form {
	my ($clip,@key,@need,%in);
	foreach my $key ( $cgi->param() ) {
		my $val;

		# �Y�t
		if ($key =~ /^clip-\d+$/) {
			$val = $cgi->param($key);
			if ($val) { $clip++; }

		# �e�L�X�g�n
		} else {

			# �����l�̏ꍇ�̓X�y�[�X�ŋ�؂�
			$val = join(" ", $cgi->param($key));

			# ���Q��/���s�ϊ�
			$key =~ s/[<>&"'\r\n]//g;
			$val =~ s/&/&amp;/g;
			$val =~ s/</&lt;/g;
			$val =~ s/>/&gt;/g;
			$val =~ s/"/&quot;/g;
			$val =~ s/'/&#39;/g;
			$val =~ s/\r\n/\t/g;
			$val =~ s/\r/\t/g;
			$val =~ s/\n/\t/g;

			# �����R�[�h�ϊ�
			if ($cf{conv_code}) {
				$key = $j->set($key)->sjis;
				$val = $j->set($val)->sjis;
			}

			# ���͕K�{
			if ($key =~ /^_(.+)/) {
				$key = $1;
				push(@need,$key);
			}
		}

		# �󂯎��L�[�̏��Ԃ��o���Ă���
		push(@key,$key);

		# %in�n�b�V���ɑ��
		$in{$key} = $val;
	}

	# post���M�`�F�b�N
	if ($cf{postonly} && $ENV{REQUEST_METHOD} ne 'POST') {
		&error("�s���ȃA�N�Z�X�ł�");
	}
	# �Y�t���ۂ̏ꍇ
	if (!$cf{attach} && $clip) {
		&error("�s���ȃA�N�Z�X�ł�");
	}

	# ���t�@�����X�ŕԂ�
	return (\@key,\@need,\%in);
}

#-----------------------------------------------------------
#  ���̓G���[�\��
#-----------------------------------------------------------
sub err_check {
	my $match2 = shift;

	# �e���v���[�g�ǂݍ���
	my ($err,$flg,$cell,%fname,%err);
	open(IN,"$cf{tmpldir}/err2.html") or &error("open err: err2.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# �e���v���[�g����
	my ($head, $loop, $foot);
	if ($tmpl =~ /(.+)<!-- cell_begin -->(.+)<!-- cell_end -->(.+)/s) {
		($head, $loop, $foot) = ($1, $2, $3);
	} else {
		&error("�e���v���[�g���s���ł�");
	}

	# ��ʓW�J
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
			$key_name = "�Y�t$1";
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
		# ���͂Ȃ�
		if ($erflg) {
			$tmp =~ s/!val!/<span class="msg">$key_name�͓��͕K�{�ł�.<\/span>/;

		# ����
		} else {

			# �Y�t�̂Ƃ�
			if ($key =~ /^clip-\d+$/i) {
				$tmp =~ s/!val!/$fname{$1}/;

			# �e�L�X�g�i�Y�t�ȊO�j
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
#  �G���[����
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
#  �t�b�^�[
#-----------------------------------------------------------
sub footer {
	my $foot = shift;

	# ���쌠�\�L�i�폜�E���ϋ֎~�j
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
#  �ꎞ�f�B���N�g���|��
#-----------------------------------------------------------
sub clean_dir {
	# �ꎞ�f�B���N�g�����ǂݎ��
	opendir(DIR,"$cf{upldir}");
	my @dir = readdir(DIR);
	closedir(DIR);

	foreach (@dir) {
		# �ΏۊO�̓X�L�b�v
		next if ($_ eq '.');
		next if ($_ eq '..');
		next if ($_ eq 'index.html');
		next if ($_ eq '.htaccess');

		# �t�@�C�����Ԏ擾
		my $mtime = (stat("$cf{upldir}/$_"))[9];

		# 1���Ԉȏ�o�߂��Ă���t�@�C���͍폜
		if (time - $mtime > 3600) {
			unlink("$cf{upldir}/$_");
		}
	}
}

#-----------------------------------------------------------
#  ���Ԏ擾
#-----------------------------------------------------------
sub get_time {
	$ENV{TZ} = "JST-9";
	my ($sec,$min,$hour,$mday,$mon,$year,$wday) = localtime(time);
	my @week  = qw|Sun Mon Tue Wed Thu Fri Sat|;
	my @month = qw|Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec|;

	# �����̃t�H�[�}�b�g
	my $date1 = sprintf("%04d/%02d/%02d(%s) %02d:%02d:%02d",
			$year+1900,$mon+1,$mday,$week[$wday],$hour,$min,$sec);
	my $date2 = sprintf("%s, %02d %s %04d %02d:%02d:%02d",
			$week[$wday],$mday,$month[$mon],$year+1900,$hour,$min,$sec) . " +0900";

	return ($date1,$date2);
}

#-----------------------------------------------------------
#  �z�X�g���擾
#-----------------------------------------------------------
sub get_host {
	# �z�X�g���擾
	my $h = $ENV{REMOTE_HOST};
	my $a = $ENV{REMOTE_ADDR};

	if ($cf{gethostbyaddr} && ($h eq "" || $h eq $a)) {
		$h = gethostbyaddr(pack("C4", split(/\./, $a)), 2);
	}
	if ($h eq "") { $h = $a; }

	# �`�F�b�N
	if ($cf{denyhost}) {
		my $flg;
		foreach ( split(/\s+/, $cf{denyhost}) ) {
			s/\./\\\./g;
			s/\*/\.\*/g;

			if ($h =~ /$_/i) { $flg++; last; }
		}
		if ($flg) { &error("�A�N�Z�X��������Ă��܂���"); }
	}

	return ($h,$a);
}

#-----------------------------------------------------------
#  �摜���T�C�Y
#-----------------------------------------------------------
sub resize {
	my ($path,$ext) = @_;

	# �T�C�Y�擾
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

	# ����
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
#  JPEG�T�C�Y�F��
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
#  GIF�T�C�Y�F��
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
#  PNG�T�C�Y�F��
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
#  BMP�T�C�Y
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

