#!/usr/local/bin/perl

#┌─────────────────────────────────
#│ YY-BOARD : admin.cgi - 2021/07/24
#│ copyright (c) kentweb, 1997-2021
#│ https://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);
use vars qw(%in %cf);
use lib "./lib";
use CGI::Session;
use Digest::SHA::PurePerl qw(sha256_base64);

# 設定ファイル認識
require "./init.cgi";
%cf = set_init();

# データ受理
%in = parse_form();

# 認証
require "./lib/login.pl";
auth_login();

# 処理分岐
if ($in{data_men}) { data_men(); }
if ($in{pass_mgr}) { pass_mgr(); }

# メニュー画面
menu_html();

#-----------------------------------------------------------
#  メニュー画面
#-----------------------------------------------------------
sub menu_html {
	header("メニューTOP");
	print <<EOM;
<div id="body">
<div class="menu-msg">選択ボタンを押してください。</div>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="sid" value="$in{sid}">
<table class="form-tbl">
<tr>
	<th>選択</th>
	<th width="280">処理メニュー</th>
</tr><tr>
	<td><input type="submit" name="data_men" value="選択"></td>
	<td>データ管理</td>
</tr><tr>
	<td><input type="submit" name="pass_mgr" value="選択"></td>
	<td>パスワード管理</td>
</tr><tr>
	<td><input type="submit" name="logoff" value="選択"></td>
	<td>ログアウト</td>
</tr>
</table>
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  記事管理
#-----------------------------------------------------------
sub data_men {
	# 修正フォーム
	if ($in{job} eq "edit" && $in{no}) {
		
		my @log;
		open(DAT,"$cf{datadir}/log.cgi");
		my $top = <DAT>;
		while (<DAT>) {
			my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ico) = split(/<>/);
			
			if ($in{no} == $no) {
				@log = ($name,$eml,$sub,$com,$url,$col,$ico);
				last;
			}
		}
		close(DAT);
		
		if (@log == 0) { err_msg("該当記事は存在しません"); }
		
		# 修正フォーム
		edit_form(@log);
	
	# 修正実行
	} elsif ($in{job} eq "edit2") {
		
		# 入力値補正
		if ($in{url} eq 'http://') { $in{url} = ''; }
		$in{sub} ||= '無題';
		
		# アイコン
		my @icon;
		foreach (@{$cf{icon}}) {
			my ($ico,$nam) = split(/,/);
			push(@icon,$ico);
		}
		
		# データオープン
		my @data;
		open(DAT,"+< $cf{datadir}/log.cgi");
		eval "flock(DAT,2);";
		my $top = <DAT>;
		while (<DAT>) {
			my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ico) = split(/<>/);

			if ($no == $in{no}) {
				$_ = "$no<>$reno<>$date<>$in{name}<>$in{email}<>$in{sub}<>$in{comment}<>$in{url}<>$host<>$pw<>$in{color}<>$icon[$in{icon}]<>\n";
			}
			push(@data,$_);
		}
		
		# 更新
		unshift(@data,$top);
		seek(DAT,0,0);
		print DAT @data;
		truncate(DAT,tell(DAT));
		close(DAT);
	
	# 削除処理
	} elsif ($in{job} eq "dele" && $in{no}) {
		
		# データオープン
		my @data;
		open(DAT,"+< $cf{datadir}/log.cgi");
		eval "flock(DAT,2);";
		my $top = <DAT>;
		while (<DAT>) {
			my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ico) = split(/<>/);
			
			# 親/子削除
			next if ($in{no} == $no or $in{no} == $reno);
			
			push(@data,$_);
		}
		
		# 更新
		unshift(@data,$top);
		seek(DAT,0,0);
		print DAT @data;
		truncate(DAT,tell(DAT));
		close(DAT);
	}
	
	# 管理を表示
	header("管理画面");
	print <<EOM;
<div id="body">
<div class="back-btn">
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="sid" value="$in{sid}">
<input type="submit" value="&lt; メニュー">
</form>
</div>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="data_men" value="1">
<input type="hidden" name="sid" value="$in{sid}">
処理：
<select name="job">
<option value="edit">編集</option>
<option value="dele">削除</option>
</select>
<input type="submit" value="送信する">
EOM

	open(IN,"$cf{datadir}/log.cgi") or err_msg("open err: log.cgi");
	my $top = <IN>;
	while (<IN>) {
		my ($no,$reno,$date,$name,$eml,$sub,$com,$url,$host,$pw,$col,$ico) = split(/<>/);
		$name = qq|<a href="mailto:$eml">$name</a>| if ($eml);
		
		if (!$reno) {
			print qq|<div class="main">|;
		} else {
			print qq|<div class="sub">|;
		}
		
		print qq|<input type="radio" name="no" value="$no">[$no]\n|;
		print qq|<b class="sub">$sub</b> 名前：<b>$name</b> 日時：$date [$host]\n|;
		print qq|<div class="com">| . cut_str($com,50) . qq|</div>\n|;
		print qq|</div>\n|;
	}
	close(IN);
	
	print <<EOM;
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  修正フォーム
#-----------------------------------------------------------
sub edit_form {
	my ($name,$eml,$sub,$com,$url,$col,$ico) = @_;
	$com =~ s|<br( /)?>|\n|g;
	$url ||= 'http://';
	
	my @col = split(/\s+/,$cf{colors});
	my $color;
	foreach (0 .. $#col) {
		if ($col == $_) {
			$color .= qq|<input type="radio" name="color" value="$_" checked>|;
		} else {
			$color .= qq|<input type="radio" name="color" value="$_">|;
		}
		$color .= qq|<span style="color:$col[$_]">■</span>\n|;
	}
	my $op_icon;
	foreach (0 .. $#{$cf{icon}}) {
		my ($fnam,$nam) = split(/,/, $cf{icon}->[$_]);
		if ($fnam eq $ico) {
			$op_icon .= qq|<option value="$_" selected>$nam</option>\n|;
		} else {
			$op_icon .= qq|<option value="$_">$nam</option>\n|;
		}
	}
	
	header("管理モード &gt; 修正フォーム");
	print <<EOM;
<div id="body">
<div class="ta-r">
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="data_men" value="1">
<input type="hidden" name="sid" value="$in{sid}">
<input type="submit" value="&lt; 戻る">
</form>
</div>
<div class="ttl">■ 編集フォーム</div>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="sid" value="$in{sid}">
<input type="hidden" name="data_men" value="1">
<input type="hidden" name="job" value="edit2">
<input type="hidden" name="no" value="$in{no}">
<table class="form-tbl">
<tr>
	<th>名前</th>
	<td><input type="text" name="name" value="$name" size="30"></td>
</tr><tr>
	<th>E-mail</th>
	<td><input type="text" name="email" value="$eml" size="30"></td>
</tr><tr>
	<th>件名</th>
	<td><input type="text" name="sub" value="$sub" size="40"></td>
</tr><tr>
	<th>コメント</th>
	<td><textarea name="comment" cols="60" rows="8">$com</textarea></td>
</tr><tr>
	<th>URL</th>
	<td><input type="text" name="url" value="$url" size="40"></td>
</tr><tr>
	<th>アイコン</th>
	<td>
		<select name="icon">
		$op_icon
		</select>
	</td>
</tr><tr>
	<th>文字色</th>
	<td>$color</td>
</tr><tr>
	<th></th>
	<td><input type="submit" value="送信する"></td>
</tr>
</table>
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  HTMLヘッダー
#-----------------------------------------------------------
sub header {
	my $ttl = shift;
	
	print <<EOM;
Content-type: text/html; charset=utf-8

<!doctype html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<link href="$cf{cmnurl}/admin.css" rel="stylesheet">
<title>$ttl</title>
</head>
<body>
<div id="head"> :: YY-BOARD 管理画面 :: </div>
EOM
}

#-----------------------------------------------------------
#  エラー画面
#-----------------------------------------------------------
sub err_msg {
	my $err = shift;
	
	header("ERROR");
	print <<EOM;
<div id="body">
<div id="err-box">
<h3>ERROR!</h3>
<p class="red">$err</p>
</div>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  文字カット for UTF-8
#-----------------------------------------------------------
sub cut_str {
	my ($str,$all) = @_;
	$str =~ s|<br( /)?>||g;
	
	my $i = 0;
	my ($ret,$flg);
	while ($str =~ /([\x00-\x7f]|[\xC0-\xDF][\x80-\xBF]|[\xE0-\xEF][\x80-\xBF]{2}|[\xF0-\xF7][\x80-\xBF]{3})/gx) {
		$i++;
		$ret .= $1;
		if ($i >= $all) {
			$flg++;
			last;
		}
	}
	$ret .= '...' if ($flg);
	
	return $ret;
}


