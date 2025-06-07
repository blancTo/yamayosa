#!/usr/local/bin/perl

#��������������������������������������������������������������������
#�� LimeCounter : list.cgi - 2011/09/28
#�� Copyright (c) KentWeb
#�� http://www.kent-web.com/
#��������������������������������������������������������������������

# ���W���[���錾
use strict;
use CGI::Carp qw(fatalsToBrowser);

# �O���t�@�C����荞��
require './init.cgi';
my %cf = &init;

# ��������
&list_data;

#-----------------------------------------------------------
#  �W�v���
#-----------------------------------------------------------
sub list_data {
	# �f�[�^�ǂݍ���
	my $all = 0;
	my (@data,@sort);
	open(IN,"$cf{idxfile}") or &error("open err: $cf{idxfile}");
	while (<IN>) {
		my ($id,$sub,$link,$file) = split(/<>/);

		open(DB,"$cf{datadir}/$id.dat");
		my $data = <DB>;
		close(DB);

		# ���O����
		my ($count, $ip) = split(/:/, $data);

		# ���v
		$all += $count;

		push(@sort,$count);
		push(@data,"$id<>$sub<>$link<>$count");
	}
	close(IN);

	# �\�[�g����
	@data = @data[sort {$sort[$b] <=> $sort[$a]} 0 .. $#sort];

	# �e���v���[�g�Ǎ�
	open(IN,"$cf{list_tmpl}") or &error("open err: $cf{list_tmpl}");
	my $tmpl = join('', <IN>);
	close(IN);

	# �e���v���[�g����
	$tmpl =~ /(.+)<!-- loop_begin -->(.+)<!-- loop_end -->(.+)/s;
	my ($head, $loop, $foot) = ($1, $2, $3);
	$head =~ s/!homepage!/$cf{homepage}/g;

	# ��ʓW�J
	print "Content-type: text/html\n\n";
	print $head;

	# �W�v���ʓW�J
	my ($i,$rk,$bef_c,$bef_r);
	foreach (@data) {
		my ($id,$item,$link,$count) = split(/<>/);
		$item = qq|<a href="$link" target="_blank">$item</a>| if ($link);
		$i++;

		my ($per,$wid);
		if ($all > 0) {
			$per = sprintf("%.1f", $count * 100 / $all);
			if ($per > 100) { $per = 100; }
			$wid = int($per * 5);
			if ($wid < 1) { $wid = 1; }
		} else {
			$per = "0.0";
			$wid = 1;
		}

		# ���ʒ�`
		if ($count ne $bef_c) { $rk = $i; } else { $rk = $bef_r; }
		$bef_c = $count;
		$bef_r = $rk;

		# �����u������
		my $tmp = $loop;
		$tmp =~ s/!item!/$item/g;
		$tmp =~ s/!rank!/$rk/g;
		$tmp =~ s/!count!/&comma($count)/eg;
		$tmp =~ s|!graph!|<img src="$cf{graph}" height="8" width="$wid"> $per%|g;
		print $tmp;
	}

	# �t�b�^�[
	$foot =~ s/!all!/&comma($all)/eg;
	&footer($foot);
}

#-----------------------------------------------------------
#  �t�b�^�[
#-----------------------------------------------------------
sub footer {
	my $foot = shift;

	# ���쌠�\�L�i�폜�E���ϋ֎~�j
	my $copy = <<EOM;
<p style="margin-top:3em;text-align:center;font-family:Verdana,Helvetica,Arial;font-size:10px;">
- <a href="http://www.kent-web.com/" target="_top">LimeCounter</a> -
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

