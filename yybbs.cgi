#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ YY-BOARD : yybbs.cgi - 2021/07/24
#│ copyright (c) KentWeb, 1997-2021
#│ https://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);

# 設定ファイル認識
require "./init.cgi";
my %cf = set_init();

# データ受理
my %in = parse_form();

# アクセス制限
passwd(%in) if ($cf{enter_pwd} ne '');

# 処理分岐
if ($in{mode} eq 'find') { find_data(); }
if ($in{mode} eq 'note') { note_page(); }
if ($in{mode} eq 'icon') { icon_page(); }
if ($in{mode} eq 'past') { past_log(); }
bbs_list();

#-----------------------------------------------------------
#  記事表示部
#-----------------------------------------------------------
sub bbs_list {
	# 返信フォーム
	read_log($in{res},'res') if ($in{res} > 0);
	
	# 記事展開
	my ($i,@log,%res,%nam,%sub,%dat,%com,%url,%col,%ico,%rno,%upd);
	open(IN,"$cf{datadir}/log.cgi") or error("open err: log.cgi");
	my $top = <IN>;
	while (<IN>) {
		my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ico) = split(/<>/);
		
		++$i if (!$reno);
		next if ($i < $in{pg} + 1);
		next if ($i > $in{pg} + $cf{pg_max});
		
		# 親記事
		if (!$reno) {
			push(@log,$no);
			$rno{$no} = 0;
			$upd{$no} = "$date<br>$name";
			
		# レス記事
		} else {
			$res{$reno} .= "$no,";
			$rno{$reno}++;
			$upd{$reno} = "$date<br>$name";
		}
		# リンク（スレッドのとき）
		if (!$in{bbs}) {
			$name = qq|<a href="mailto:$eml">$name</a>| if ($eml);
			$url &&= qq|<a href="$url" target="_blank"><img src="$cf{cmnurl}/home.png" class="icon" alt="home"></a>|;
			$com = auto_link($com) if ($cf{autolink});
			$in{bbs} = 0;
		}
		
		# ハッシュ化
		$nam{$no} = $name;
		$sub{$no} = $sub;
		$dat{$no} = $date;
		$com{$no} = $com;
		$col{$no} = $col;
		$url{$no} = $url;
		$ico{$no} = $ico;
	}
	close(IN);
	
	# 繰越ボタン作成
	my $page_btn = make_pgbtn($i,$in{pg},"&amp;bbs=$in{bbs}");
	
	# クッキー取得
	my @cook = get_cookie($cf{cookie_id});
	$cook[2] ||= 'http://';
	
	# 色選択ボタン
	my @col = split(/\s+/,$cf{colors});
	my $color;
	foreach (0 .. $#col) {
		if ($_ == $cook[3]) {
			$color .= qq|<input type="radio" name="color" value="$_" checked>|;
		} else {
			$color .= qq|<input type="radio" name="color" value="$_">|;
		}
		$color .= qq|<span style="color:$col[$_]">■</span>\n|;
	}
	# アイコンプルダウン
	my $op_icon;
	foreach (0 .. $#{$cf{icon}}) {
		my ($ico,$nam) = split(/,/,$cf{icon}[$_]);
		if ($cook[4] == $_) {
			$op_icon .= qq|<option value="$_" selected>$nam</option>\n|;
		} else {
			$op_icon .= qq|<option value="$_">$nam</option>\n|;
		}
	}
	
	# カウンタ
	my $counter = bbs_count() if ($cf{counter});
	
	# home or logoff
	my $home = $cf{enter_pwd} eq '' ? $cf{homepage} : "$cf{bbs_cgi}?mode=logoff";
	
	# テンプレート
	my ($pfile,$cfile,$resloop);
	if (!$in{bbs}) {
		$pfile = 'bbs.html';
		
		open(IN,"$cf{tmpldir}/bbs-res.html") or error("open err: bbs-res.html");
		$resloop = join('',<IN>);
		close(IN);
	} else {
		$pfile = 'topic.html';
	}
	open(IN,"$cf{tmpldir}/$pfile") or error("open err: $pfile");
	my $tmpl = join('',<IN>);
	close(IN);
	
	# 画像認証作成
	my ($str_plain,$str_crypt);
	if ($cf{use_captcha} > 0) {
		require $cf{captcha_pl};
		($str_plain,$str_crypt) = cap::make( $cf{captcha_key}, $cf{cap_len} );
	} else {
		$tmpl =~ s|<!-- captcha -->.+?<!-- /captcha -->||s;
	}
	
	# 文字置換
	$tmpl =~ s/!bbs_title!/$cf{bbs_title}/g;
	$tmpl =~ s|!icon:(\w+\.\w+)!|<img src="$cf{cmnurl}/$1" alt="$1" class="icon">|g;
	$tmpl =~ s|!bbs_css!|$cf{cmnurl}/bbs.css|g;
	$tmpl =~ s|!bbs_js!|$cf{cmnurl}/bbs.js|g;
	$tmpl =~ s/!([a-z]+_cgi)!/$cf{$1}/g;
	$tmpl =~ s/!homepage!/$home/g;
	$tmpl =~ s/!page_btn!/$page_btn/g;
	$tmpl =~ s/!name!/$cook[0]/;
	$tmpl =~ s/!email!/$cook[1]/;
	$tmpl =~ s/!url!/$cook[2]/;
	$tmpl =~ s/!str_crypt!/$str_crypt/g;
	$tmpl =~ s/!color!/$color/g;
	$tmpl =~ s/<!-- op_icon -->/$op_icon/g;
	$tmpl =~ s/!sub!//g;
	$tmpl =~ s/!reno!//g;
	$tmpl =~ s/!counter!/$counter/g;
	
	if ($cf{icon_mode} == 0) {
		$tmpl =~ s|<!-- pop_icon -->.+?<!-- /pop_icon -->||s;
	}
	
	# テンプレート分割
	my ($head,$loop,$foot) = $tmpl =~ m|(.+)<!-- loop -->(.+?)<!-- /loop -->(.+)|s
			? ($1,$2,$3)
			: error("テンプレート不正");
	
	# ノンアイコン
	if ($cf{icon_mode} == 0) {
		$loop =~ s/!icon!//g;
		$resloop =~ s/!icon!//g;
	}
	
	# ヘッダ表示
	print "Content-type: text/html; charset=utf-8\n\n";
	print $head;
	
	# 記事表示
	foreach (@log) {
		# レス
		my ($res,$n);
		foreach my $r ( split(/,/,$res{$_}) ) {
			$n++;
			
			my $tmp = $resloop;
			$tmp =~ s/!art-ttl!/$sub{$r}/g;
			$tmp =~ s/!name!/$nam{$r}/g;
			$tmp =~ s/!url!/$url{$r}/g;
			$tmp =~ s/!date!/$dat{$r}/g;
			$tmp =~ s/!num!/$r/g;
			$tmp =~ s|!comment!|<span style="color:$col[$col{$r}]">$com{$r}</span>|g;
			$tmp =~ s|!icon!|<img src="$cf{cmnurl}/face/$ico{$r}" class="image" alt="$ico{$r}">|g;
			$tmp =~ s|!icon:(\w+\.\w+)!|<img src="$cf{cmnurl}/$1" alt="$1" class="icon">|g;
			$tmp =~ s/!bbs_cgi!/$cf{bbs_cgi}/g;
			$res .= $tmp;
		}
		
		# 親
		my $tmp = $loop;
		$tmp =~ s/!art-ttl!/$sub{$_}/g;
		$tmp =~ s/!name!/$nam{$_}/g;
		$tmp =~ s/!url!/$url{$_}/g;
		$tmp =~ s/!date!/$dat{$_}/g;
		$tmp =~ s/!num!/$_/g;
		$tmp =~ s/!pg!/$in{pg} eq '' ? '0' : $in{pg}/ge;
		$tmp =~ s/!bbs!/$in{bbs} eq '' ? '0' : $in{bbs}/ge;
		$tmp =~ s|!comment!|<span style="color:$col[$col{$_}]">$com{$_}</span>|g;
		$tmp =~ s/<!-- res -->/$res/g;
		$tmp =~ s|!icon!|<img src="$cf{cmnurl}/face/$ico{$_}" class="image" alt="$ico{$_}">|g;
		$tmp =~ s/!bbs_cgi!/$cf{bbs_cgi}/g;
		$tmp =~ s/!res!/$rno{$_}/g;
		$tmp =~ s/!update!/$upd{$_}/g;
		print $tmp;
	}
	
	# フッタ
	footer($foot);
}

#-----------------------------------------------------------
#  記事閲覧（返信フォーム）
#-----------------------------------------------------------
sub read_log {
	my ($num,$btn) = @_;
	if ($num =~ /^(\d+)$/) { $num = $1; }
	
	my ($resub,@log);
	open(IN,"$cf{datadir}/log.cgi") or error("open err: log.cgi");
	my $top = <IN>;
	while (<IN>) {
		my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ico) = split(/<>/);
		
		if ($num == $no || $num == $reno) {
			push(@log,$_);
		}
		if ($num == $no) {
			if ($sub =~ /^Re:/) { $resub = $sub } else { $resub = "Re: $sub"; }
		}
	}
	close(IN);
	
	# クッキー取得
	my @cook = get_cookie($cf{cookie_id});
	$cook[2] ||= 'http://';
	
	# 色選択ボタン
	my @col = split(/\s+/,$cf{colors});
	my $color;
	foreach (0 .. $#col) {
		if ($_ == $cook[3]) {
			$color .= qq|<input type="radio" name="color" value="$_" checked>|;
		} else {
			$color .= qq|<input type="radio" name="color" value="$_">|;
		}
		$color .= qq|<span style="color:$col[$_]">■</span>\n|;
	}
	# アイコンプルダウン
	my $op_icon;
	foreach (0 .. $#{$cf{icon}}) {
		my ($ico,$nam) = split(/,/,$cf{icon}->[$_]);
		if ($cook[4] == $_) {
			$op_icon .= qq|<option value="$_" selected>$nam</option>\n|;
		} else {
			$op_icon .= qq|<option value="$_">$nam</option>\n|;
		}
	}
	
	# home or logoff
	my $home = $cf{enter_pwd} eq '' ? $cf{homepage} : "$cf{bbs_cgi}?mode=logoff";
	
	# テンプレート読込
	open(IN,"$cf{tmpldir}/read.html") or error("open err: read.html");
	my $tmpl = join('',<IN>);
	close(IN);
	
	if ($btn) { $tmpl =~ s|<div id="reg-box" style="display:none;">|<div id="reg-box">|; }
	
	# 画像認証作成
	my ($str_plain,$str_crypt);
	if ($cf{use_captcha} > 0) {
		require $cf{captcha_pl};
		($str_plain,$str_crypt) = cap::make($cf{captcha_key},$cf{cap_len});
	} else {
		$tmpl =~ s|<!-- captcha -->.+?<!-- /captcha -->||s;
	}
	
	# 文字置換
	$tmpl =~ s/!bbs_title!/$cf{bbs_title}/g;
	$tmpl =~ s/!([a-z]+_cgi)!/$cf{$1}/g;
	$tmpl =~ s|!bbs_css!|$cf{cmnurl}/bbs.css|g;
	$tmpl =~ s|!bbs_js!|$cf{cmnurl}/bbs.js|g;
	$tmpl =~ s/!homepage!/$home/g;
	$tmpl =~ s/!name!/$cook[0]/;
	$tmpl =~ s/!email!/$cook[1]/;
	$tmpl =~ s/!url!/$cook[2]/;
	$tmpl =~ s/!str_crypt!/$str_crypt/g;
	$tmpl =~ s/!color!/$color/g;
	$tmpl =~ s/!sub!/$resub/g;
	$tmpl =~ s/!reno!/$num/g;
	$tmpl =~ s/<!-- op_icon -->/$op_icon/g;
	$tmpl =~ s|<!-- pop_icon -->.+?<!-- /pop_icon -->||s if ($cf{icon_mode} == 0);
	$tmpl =~ s/!bbs!/$in{bbs} eq '' ? '0' : $in{bbs}/ge;
	$tmpl =~ s/!pg!/$in{pg} eq '' ? '0' : $in{pg}/ge;
	
	# テンプレート分割
	my ($head,$loop,$foot) = $tmpl =~ m|(.+)<!-- loop -->(.+?)<!-- /loop -->(.+)|s
			? ($1,$2,$3)
			: error("テンプレートが不正です");
	
	# ノンアイコン
	$loop =~ s/!icon!//g if ($cf{icon_mode} == 0);
	
	# ヘッダ表示
	print "Content-type: text/html; charset=utf-8\n\n";
	print $head;
	
	# 記事
	foreach (@log) {
		my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ico) = split(/<>/);
		$name = qq|<a href="mailto:$eml">$name</a>| if ($eml);
		$com  = auto_link($com) if ($cf{autolink});
		$url &&= qq|<a href="$url" target="_blank"><img src="$cf{cmnurl}/home.png" class="icon" alt="home"></a>|;
		
		my $tmp = $loop;
		$tmp =~ s/!num!/$no/g;
		$tmp =~ s/!art-ttl!/$sub/g;
		$tmp =~ s/!date!/$date/g;
		$tmp =~ s/!name!/$name/g;
		$tmp =~ s/!url!/$url/g;
		$tmp =~ s|!comment!|<span style="color:$col[$col]">$com</span>|g;
		$tmp =~ s|!icon!|<img src="$cf{cmnurl}/face/$ico" class="image" alt="$ico">|g;
		print $tmp;
	}
	
	# フッタ
	footer($foot);
}

#-----------------------------------------------------------
#  ワード検索
#-----------------------------------------------------------
sub find_data {
	# 条件
	$in{cond} =~ s/\D//g;
	
	# 検索条件プルダウン
	my %op = (1 => 'AND', 0 => 'OR');
	my $op_cond;
	foreach (1,0) {
		if ($in{cond} eq $_) {
			$op_cond .= qq|<option value="$_" selected>$op{$_}</option>\n|;
		} else {
			$op_cond .= qq|<option value="$_">$op{$_}</option>\n|;
		}
	}
	
	# 検索実行
	my ($hit,@log) = search("$cf{datadir}/log.cgi") if ($in{word} ne '');
	
	# 文字色
	my @col = split(/\s+/,$cf{colors});
	
	# テンプレート
	open(IN,"$cf{tmpldir}/find.html") or error("open err: find.html");
	my $tmpl = join('',<IN>);
	close(IN);
	
	$tmpl =~ s|!bbs_css!|$cf{cmnurl}/bbs.css|g;
	$tmpl =~  s/!bbs_cgi!/$cf{bbs_cgi}/g;
	$tmpl =~ s/<!-- op_cond -->/$op_cond/;
	$tmpl =~ s/!word!/$in{word}/;
	$tmpl =~ s/!bbs!/$in{bbs} ne '' ? $in{bbs} : '0'/ge;
	
	# 分割
	my ($head,$loop,$foot) = $tmpl =~ m|(.+)<!-- loop -->(.+?)<!-- /loop -->(.+)|s
			? ($1,$2,$3)
			: error("テンプレートが不正です");
	
	# ノンアイコン
	$loop =~ s/!icon!//g if ($cf{icon_mode} == 0);
	
	# ヘッダ部
	print "Content-type: text/html; charset=utf-8\n\n";
	print $head;
	
	# ループ部
	foreach my $log (@log) {
		my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ico) = split(/<>/,$log);
		$name = qq|<a href="mailto:$eml">$name</a>| if ($eml);
		$com  = auto_link($com) if ($cf{autolink});
		$url &&= qq|<a href="$url" target="_blank"><img src="$cf{cmnurl}/home.png" class="icon" alt="home"></a>|;
		
		my $tmp = $loop;
		$tmp =~ s/!art-ttl!/$sub/g;
		$tmp =~ s/!date!/$date/g;
		$tmp =~ s/!name!/$name/g;
		$tmp =~ s/!url!/$url/g;
		$tmp =~ s/!num!/$no/g;
		$tmp =~ s|!comment!|<span style="color:$col[$col]">$com</span>|g;
		$tmp =~ s|!icon!|<img src="$cf{cmnurl}/face/$ico" class="image" alt="$ico">|g;
		print $tmp;
	}
	
	# フッタ
	footer($foot);
}

#-----------------------------------------------------------
#  検索実行
#-----------------------------------------------------------
sub search {
	my ($file,$list,$stat) = @_;
	
	# キーワードを配列化
	$in{word} =~ s/　/ /g;
	my @wd = split(/\s+/,$in{word});
	
	# UTF-8定義
	my $byte1 = '[\x00-\x7f]';
	my $byte2 = '[\xC0-\xDF][\x80-\xBF]';
	my $byte3 = '[\xE0-\xEF][\x80-\xBF]{2}';
	my $byte4 = '[\xF0-\xF7][\x80-\xBF]{3}';
	
	# 検索処理
	my ($i,@log);
	open(IN,"$file") or error("open err: $file");
	my $top = <IN> if (!$stat);
	while (<IN>) {
		my ($no,$reno,$date,$nam,$eml,$sub,$com,$url,$hos,$pw,$col,$ico) = split(/<>/);
		
		my $flg;
		foreach my $wd (@wd) {
			if ("$nam $eml $sub $com $url" =~ /^(?:$byte1|$byte2|$byte3|$byte4)*?\Q$wd\E/i) {
				$flg++;
				if ($in{cond} == 0) { last; }
			} else {
				if ($in{cond} == 1) { $flg = 0; last; }
			}
		}
		next if (!$flg);
		
		$i++;
		if ($list > 0) {
			next if ($i < $in{pg} + 1);
			next if ($i > $in{pg} + $list);
		}
		
		push(@log,$_);
	}
	close(IN);
	
	# 検索結果
	return ($i,@log);
}

#-----------------------------------------------------------
#  留意事項表示
#-----------------------------------------------------------
sub note_page {
	open(IN,"$cf{tmpldir}/note.html") or error("open err: note.html");
	my $tmpl = join('',<IN>);
	close(IN);
	
	$tmpl =~ s|!bbs_css!|$cf{cmnurl}/bbs.css|g;
	
	print "Content-type: text/html; charset=utf-8\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  アイコン一覧
#-----------------------------------------------------------
sub icon_page {
	# 画像サイズ再定義
	$cf{max_img_w} = 40;
	$cf{max_img_h} = 40;
	
	# テンプレート認識
	open(IN,"$cf{tmpldir}/icon.html") or error("open err: icon.html");
	my $tmpl = join('',<IN>);
	close(IN);
	
	# 文字置換
	$tmpl =~ s/!([a-z]+_cgi)!/$cf{$1}/g;
	$tmpl =~ s|!bbs_css!|$cf{cmnurl}/bbs.css|g;
	
	# テンプレート分割
	my ($head,$loop,$foot) = $tmpl =~ m|(.+)<!-- photo -->(.+?)<!-- /photo -->(.+)|s
			? ($1,$2,$3)
			: error("テンプレートが不正です");
	
	# 画面展開
	print "Content-type: text/html; charset=utf-8\n\n";
	print $head;
	
	foreach (0 .. $#{$cf{icon}}) {
		my ($ico,$cap) = split(/,/,$cf{icon}[$_]);
		
		my $tmp = $loop;
		$tmp =~ s|!image!|<img src="$cf{cmnurl}/face/$ico" alt="$ico">|g;
		$tmp =~ s/!caption!/$cap/g;
		print $tmp;
	}
	
	# フッタ
	print $foot;
	exit;
}

#-----------------------------------------------------------
#  過去ログ画面
#-----------------------------------------------------------
sub past_log {
	# 過去ログ番号
	open(IN,"$cf{nofile}") or error("open err: $cf{nofile}");
	my $pastnum = <IN>;
	close(IN);
	
	my $pastnum = sprintf("%04d",$pastnum);
	$in{pno} =~ s/\D//g;
	$in{pno} ||= $pastnum;
	
	# プルダウンタグ作成
	my $op_pno;
	for ( my $i = $pastnum; $i > 0; $i-- ) {
		$i = sprintf("%04d",$i);
		
		if ($in{pno} == $i) {
			$op_pno .= qq|<option value="$i" selected>$i</option>\n|;
		} else {
			$op_pno .= qq|<option value="$i">$i</option>\n|;
		}
	}
	
	# ページ数
	my $pg = $in{pg} || 0;
	
	# 初期化
	my ($hit,$page_btn,$hit,@log,%res);
	
	# 対象ログ定義
	my $file = "$cf{pastdir}/" . sprintf("%04d", $in{pno}) . ".cgi";
	
	# ワード検索
	if ($in{find} && $in{word} ne '') {
		# 検索
		($hit,@log) = search($file,$in{list},'past');
		
		# 結果
		$page_btn = "検索結果：<b>$hit</b>件 &nbsp;&nbsp;" . pgbtn_old($hit,$in{pno},$pg,$in{list},'find');
	
	# ログ一覧
	} else {
		my $pg_max = $cf{pg_max} * 2;
		
		# 過去ログオープン
		my $i = 0;
		open(IN,"$file") or error("open err: $file");
		while(<IN>) {
			my ($no,$reno,$date,$nam,$eml,$sub,$com,$url,$hos,$pw,$col,$ico) = split(/<>/);
			
			++$i if ($reno eq '');
			next if ($i < $pg + 1);
			next if ($i > $pg + $pg_max);
			
			if ($reno) {
				$res{$reno} .= "$no<>$reno<>$date<>$nam<>$eml<>$sub<>$com<>$url<>$col<>$ico\0";
				next;
			}
			push(@log,$_);
		}
		close(IN);
		
		# 繰越ボタン作成
		$page_btn = pgbtn_old($i,$in{pno},$pg,$pg_max);
	}
	
	# プルダウン作成（検索条件）
	my %op = make_op();
	
	# テンプレート読み込み
	open(IN,"$cf{tmpldir}/past.html") or error("open err: past.html");
	my $tmpl = join('',<IN>);
	close(IN);
	
	open(IN,"$cf{tmpldir}/bbs-res.html") or error("open err: bbs-res.html");
	my $restmpl = join('',<IN>);
	close(IN);
	
	# 文字置換
	$tmpl =~ s|!bbs_css!|$cf{cmnurl}/bbs.css|g;
	$tmpl =~ s/!past_num!/$in{pno}/g;
	$tmpl =~ s/!bbs_url!//g;
	$tmpl =~ s/!([a-z]+_cgi)!/$cf{$1}/g;
	$tmpl =~ s/<!-- op_pno -->/$op_pno/g;
	$tmpl =~ s/<!-- op_(\w+) -->/$op{$1}/g;
	$tmpl =~ s/!word!/$in{word}/g;
	$tmpl =~ s/!page_btn!/$page_btn/g;
	$tmpl =~ s/!bbs!/$in{bbs} ne '' ? $in{bbs} : '0'/ge;
	
	# テンプレート分割
	my ($head,$loop,$foot) = $tmpl =~ m|(.+)<!-- loop -->(.+?)<!-- /loop -->(.+)|s
			? ($1,$2,$3)
			: error("テンプレート不正");
	
	# ノンアイコン
	$loop =~ s/!icon!//g if ($cf{icon_mode} == 0);
	
	if ($in{change}) { $in{word} = ''; }
	
	# 文字色
	my @col = split(/\s+/,$cf{colors});
	
	# 画面表示
	print "Content-type: text/html; charset=utf-8\n\n";
	print $head;
	foreach (@log) {
		my ($no,$reno,$date,$nam,$eml,$sub,$com,$url,$hos,$pw,$col,$ico) = split(/<>/);
		$nam = qq|<a href="mailto:$eml">$nam</a>| if ($eml);
		$com = auto_link($com) if ($cf{autolink});
		$url &&= qq|<a href="$url" target="_blank"><img src="$cf{cmnurl}/home.png" class="icon" alt="home"></a>|;
		
		# レス
		my $res;
		foreach my $log ( split(/\0/, $res{$no}) ) {
			my ($no,$reno,$date,$nam,$eml,$sub,$com,$url,$col,$ico) = split(/<>/, $log);
			$nam = qq|<a href="mailto:$eml">$nam</a>| if ($eml);
			$com = auto_link($com) if ($cf{autolink});
			$url &&= qq|<a href="$url" target="_blank"><img src="$cf{cmnurl}/home.png" class="icon" alt="home"></a>|;
			
			my $tmp = $restmpl;
			$tmp =~ s/!art-ttl!/$sub/g;
			$tmp =~ s/!name!/$nam/g;
			$tmp =~ s/!date!/$date/g;
			$tmp =~ s/!num!/$no/g;
			$tmp =~ s/!url!/$url/g;
			$tmp =~ s|!comment!|<span style="color:$col[$col]">$com</span>|g;
			$tmp =~ s|!icon!|<img src="$cf{cmnurl}/face/$ico" class="image" alt="$ico">|g;
			$tmp =~ s|!icon:(\w+\.\w+)!|<img src="$cf{cmnurl}/$1" alt="" class="icon">|g;
			$res .= $tmp;
		}
		
		my $tmp = $loop;
		$tmp =~ s/!art-ttl!/$sub/g;
		$tmp =~ s/!date!/$date/g;
		$tmp =~ s/!name!/$nam/g;
		$tmp =~ s/!url!/$url/g;
		$tmp =~ s|!comment!|<span style="color:$col[$col]">$com</span>|g;
		$tmp =~ s|!icon!|<img src="$cf{cmnurl}/face/$ico" class="image" alt="$ico">|g;
		$tmp =~ s|!icon:(\w+\.\w+)!|<img src="$cf{cmnurl}/$1" alt="$1" class="icon">|g;
		$tmp =~ s/!num!/$no/g;
		$tmp =~ s/<!-- res -->/<blockquote>$res<\/blockquote>/g if ($res);
		print $tmp;
	}
	
	# フッタ
	footer($foot);
}

#-----------------------------------------------------------
#  URLエンコード
#-----------------------------------------------------------
sub url_enc {
	local($_) = @_;
	
	s/(\W)/'%' . unpack('H2', $1)/eg;
	s/\s/+/g;
	$_;
}

#-----------------------------------------------------------
#  繰越ボタン作成 [ 過去ログ ]
#-----------------------------------------------------------
sub pgbtn_old {
	my ($i,$pno,$pg,$list,$stat) = @_;
	
	# ページ繰越定義
	my $next = $pg + $list;
	my $back = $pg - $list;
	
	my $link;
	if ($stat eq 'find') {
		my $wd = url_enc($in{word});
		$link = "$cf{bbs_cgi}?mode=$in{mode}&amp;pno=$pno&amp;find=1&amp;word=$wd&amp;list=$list";
	} else {
		$link = "$cf{bbs_cgi}?mode=$in{mode}&amp;pno=$pno";
	}
	
	# ページ繰越ボタン作成
	my $pg_btn;
	if ($back >= 0 || $next < $i) {
		$pg_btn .= "Page: ";
		
		my ($x, $y) = (1, 0);
		while ($i > 0) {
			if ($pg == $y) {
				$pg_btn .= qq(| <b>$x</b> );
			} else {
				$pg_btn .= qq(| <a href="$link&amp;pg=$y">$x</a> );
			}
			$x++;
			$y += $list;
			$i -= $list;
		}
		$pg_btn .= "|";
	}
	return $pg_btn;
}

#-----------------------------------------------------------
#  プルダウン作成 [ 検索条件 ]
#-----------------------------------------------------------
sub make_op {
	my %op;
	my %cond = (1 => 'AND', 0 => 'OR');
	foreach (1,0) {
		if ($in{cond} eq $_) {
			$op{cond} .= qq|<option value="$_" selected>$cond{$_}</option>\n|;
		} else {
			$op{cond} .= qq|<option value="$_">$cond{$_}</option>\n|;
		}
	}
	for ( my $i = 10; $i <= 30; $i += 5 ) {
		if ($in{list} == $i) {
			$op{list} .= qq|<option value="$i" selected>$i件</option>\n|;
		} else {
			$op{list} .= qq|<option value="$i">$i件</option>\n|;
		}
	}
	return %op;
}

#-----------------------------------------------------------
#  カウンタ処理
#-----------------------------------------------------------
sub bbs_count {
	# IP取得
	my $addr = $ENV{REMOTE_ADDR};
	
	# 閲覧時のみカウントアップ
	my $cntup = $in{mode} eq '' ? 1 : 0;
	
	# カウントファイルを読みこみ
	open(LOG,"+< $cf{datadir}/count.dat") or error("open err: count.dat");
	eval "flock(LOG,2);";
	my $count = <LOG>;
	
	# IPチェックとログ破損チェック
	my ($cnt,$ip) = split(/:/,$count);
	if ($addr eq $ip or $cnt eq "") { $cntup = 0; }
	
	# カウントアップ
	if ($cntup) {
		$cnt++;
		seek(LOG,0,0);
		print LOG "$cnt:$addr";
		truncate(LOG,tell(LOG));
	}
	close(LOG);
	
	# 桁数調整
	while(length($cnt) < $cf{mini_fig}) { $cnt = '0' . $cnt; }
	my @cnts = split(//,$cnt);
	
	# GIFカウンタ表示
	my $counter;
	if ($cf{counter} == 2) {
		foreach (0 .. $#cnts) {
			$counter .= qq|<img src="$cf{gif_path}/$cnts[$_].gif" alt="$cnts[$_]">|;
		}
	
	# テキストカウンタ表示
	} else {
		$counter = $cnt;
	}
	return $counter;
}

#-----------------------------------------------------------
#  自動リンク
#-----------------------------------------------------------
sub auto_link {
	my $text = shift;
	
	$text =~ s/(s?https?:\/\/([\w-.!~*'();\/?:\@=+\$,%#]|&amp;)+)/<a href="$1" target="_blank">$1<\/a>/g;
	return $text;
}

#-----------------------------------------------------------
#  著作権表記（削除・改変を禁ず）
#-----------------------------------------------------------
sub footer {
	my ($foot) = @_;
	
	my $copy = <<EOM;
<p style="margin-top:3em;text-align:center;font-family:Verdana,Helvetica,Arial;font-size:10px;">
	- <a href="https://www.kent-web.com/" target="_top">YY-BOARD</a> -
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
#  繰越ボタン作成
#-----------------------------------------------------------
sub make_pgbtn {
	my ($i,$pg,$stat) = @_;
	
	# ページ繰越定義
	$cf{pg_max} ||= 10;
	my $next = $pg + $cf{pg_max};
	my $back = $pg - $cf{pg_max};
	
	# ページ繰越ボタン作成
	my @pg;
	if ($back >= 0 || $next < $i) {
		my $flg;
		my ($w,$x,$y,$z) = (0,1,0,$i);
		while ($z > 0) {
			if ($pg == $y) {
				$flg++;
				push(@pg,qq!<li><span>$x</span></li>!);
			} else {
				push(@pg,qq!<li><a href="$cf{bbs_cgi}?pg=$y$stat">$x</a></li>!);
			}
			$x++;
			$y += $cf{pg_max};
			$z -= $cf{pg_max};
			
			if ($flg) { $w++; }
			last if ($w >= 5 && @pg >= 10);
		}
	}
	while( @pg >= 11 ) { shift(@pg); }
	my $ret = join('',@pg);
	if ($back >= 0) {
		$ret = qq!<li><a href="$cf{bbs_cgi}?pg=$back$stat">&laquo;</a></li>\n! . $ret;
	}
	if ($next < $i) {
		$ret .= qq!<li><a href="$cf{bbs_cgi}?pg=$next$stat">&raquo;</a></li>\n!;
	}
	
	# 結果を返す
	return $ret ? qq|<ul class="pager">$ret</ul>| : '';
}

#-----------------------------------------------------------
#  掲示板タイプ
#-----------------------------------------------------------
sub bbstype {
	my $loop = shift;
	
	$in{type} ||= 1;
	my $ret;
	foreach ( sort{ $a <=> $b } keys %{$cf{bbs_type}} ) {
		my $tmp = $loop;
		
		if ($in{type} == $_) {
			$tmp =~ s/<.+>/<b>$cf{bbs_type}{$_}<\/b>/g;
		} else {
			$tmp =~ s/!bbs_cgi!/$cf{bbs_cgi}/g;
			$tmp =~ s/!type!/$_/g;
			$tmp =~ s/!bbstype!/$cf{bbs_type}{$_}/g;
		}
		$ret .= $tmp;
	}
	return $ret;
}

#-----------------------------------------------------------
#  クッキー取得
#-----------------------------------------------------------
sub get_cookie {
	my $cook_id = shift;
	
	# クッキー取得
	my $cook = $ENV{HTTP_COOKIE};
	
	# 該当IDを取り出す
	my %cook;
	foreach ( split(/;/,$cook) ) {
		my ($key,$val) = split(/=/);
		$key =~ s/\s//g;
		$cook{$key} = $val;
	}
	
	# URLデコード
	my @cook;
	foreach ( split(/<>/,$cook{$cook_id}) ) {
		s/%([0-9A-Fa-f][0-9A-Fa-f])/pack("H2", $1)/eg;
		s/[&"'<>]//g;
		
		push(@cook,$_);
	}
	return @cook;
}

#-----------------------------------------------------------
#  クッキー発行
#-----------------------------------------------------------
sub set_cookie {
	my $cook_id = shift;
	my @data = @_;
	
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,undef,undef) = gmtime(time + 60*24*60*60);
	my @mon  = qw|Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec|;
	my @week = qw|Sun Mon Tue Wed Thu Fri Sat|;
	
	# 時刻フォーマット
	my $gmt = sprintf("%s, %02d-%s-%04d %02d:%02d:%02d GMT",
				$week[$wday],$mday,$mon[$mon],$year+1900,$hour,$min,$sec);
	
	# URLエンコード
	my $cook;
	foreach (@data) {
		s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
		$cook .= "$_<>";
	}
	
	print "Set-Cookie: $cook_id=$cook; expires=$gmt\n";
}



