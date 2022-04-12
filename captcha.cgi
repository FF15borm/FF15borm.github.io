#!/usr/local/bin/perl

#┌─────────────────────────────
#│ 画像認証作成ファイル v3.3
#│ captcha.cgi - 2019/11/10
#│ copyright (c) kentweb
#│ https://www.kent-web.com/
#└─────────────────────────────

# モジュール宣言
use strict;
use lib "./lib";
use Crypt::RC4;

# 外部ファイル取り込み
require './init.cgi';
my %cf = set_init();

# パラメータ受け取り
my $buf = $ENV{QUERY_STRING};
$buf =~ s/[<>&"'\s]//g;
err_img() if (!$buf);

# 復号
my $plain = decrypt($cf{cap_len});

# 認証画像作成
if ($cf{use_captcha} == 2) {
	require $cf{captsec_pl};
	load_capsec($plain,"$cf{bin_dir}/$cf{font_ttl}");
} else {
	load_pngren($plain,"$cf{bin_dir}/$cf{si_png}");
}

#-----------------------------------------------------------
#  認証画像作成 [ライブラリ版]
#-----------------------------------------------------------
sub load_pngren {
	my ($plain,$sipng) = @_;
	
	# 数字
	my @img = split(//,$plain);
	
	# 表示開始
	require $cf{pngren_pl};
	pngren::PngRen($sipng,\@img);
	exit;
}

#-----------------------------------------------------------
#  復号
#-----------------------------------------------------------
sub decrypt {
	my $caplen = shift;
	
	# 復号
	$buf =~ s/N/\n/g;
	$buf =~ s/([0-9A-Fa-f]{2})/pack('H2',$1)/eg;
	my $plain = RC4($cf{captcha_key},$buf);
	
	# 先頭の数字を抽出
	$plain =~ s/^(\d{$caplen}).*/$1/ or err_img();
	return $plain;
}

#-----------------------------------------------------------
#  エラー処理
#-----------------------------------------------------------
sub err_img {
	# エラー画像
	my @err = qw{
		47 49 46 38 39 61 2d 00 0f 00 80 00 00 00 00 00 ff ff ff 2c
		00 00 00 00 2d 00 0f 00 00 02 49 8c 8f a9 cb ed 0f a3 9c 34
		81 7b 03 ce 7a 23 7c 6c 00 c4 19 5c 76 8e dd ca 96 8c 9b b6
		63 89 aa ee 22 ca 3a 3d db 6a 03 f3 74 40 ac 55 ee 11 dc f9
		42 bd 22 f0 a7 34 2d 63 4e 9c 87 c7 93 fe b2 95 ae f7 0b 0e
		8b c7 de 02	00 3b
	};
	
	print "Content-type: image/gif\n\n";
	foreach (@err) {
		print pack('C*',hex($_));
	}
	exit;
}

