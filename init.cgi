# モジュール宣言/変数初期化
use strict;
my %cf;
#┌─────────────────────────────────
#│ YY-BOARD : init.cgi - 2021/07/24
#│ copyright (c) kentweb, 1997-2021
#│ https://www.kent-web.com/
#└─────────────────────────────────
$cf{version} = 'YY-BOARD v10.2';
#┌─────────────────────────────────
#│ [注意事項]
#│ 1. このプログラムはフリーソフトです。このプログラムを使用した
#│    いかなる損害に対して作者は一切の責任を負いません。
#│ 2. 設置に関する質問はサポート掲示板にお願いいたします。
#│    直接メールによる質問は一切お受けいたしておりません。
#└─────────────────────────────────

#===========================================================
# ■ 設定項目
#===========================================================

# パスワード制限をする場合入室パスワード設定
# → 空欄の場合はパスワード制限なし
$cf{enter_pwd} = '';

# パスワード制限時のセッションの許容時間（分単位）
# → 入室後からアクセス可能時間
$cf{sestime} = 60;

# 掲示板タイトル
$cf{bbs_title} = "掲示板 - YY-BOARD";

# データディレクトリ【サーバパス】
$cf{datadir} = './data';

# 本体ファイル【URLパス】
$cf{bbs_cgi} = './yybbs.cgi';

# 更新ファイル【URLパス】
$cf{regist_cgi} = './regist.cgi';

# 管理ファイル【URLパス】
$cf{admin_cgi} = './admin.cgi';

# テンプレートディレクトリ【サーバパス】
$cf{tmpldir} = './tmpl';

# 共通ディレクトリ【URLパス】
$cf{cmnurl} = './cmn';

# 戻り先【URLパス】
$cf{homepage} = "../index.html";

# 最大記録記事数
$cf{max} = 100;

# アイコンモード機能
# 0 : アイコン不使用
# 1 : アイコン使用
$cf{icon_mode} = 1;

# アイコンを定義
# → 前にファイル名、後にアイコン名をコンマで区切る
$cf{icon} = [
	'bear.gif,くま',
	'cat.gif,ねこ',
	'cow.gif,うし',
	'dog.gif,いぬ',
	'fox.gif,きつね',
	'hituji.gif,ひつじ',
	'monkey.gif,さる',
	'zou.gif,ぞう',
	'mouse.gif,ねずみ',
	'panda.gif,パンダ',
	'pig.gif,ぶた',
	'usagi.gif,うさぎ',
	];

# 管理者専用アイコン機能 (0=no 1=yes)
# (使い方) 記事投稿時に「管理者アイコン」を選択し暗証キーに「管理パスワード」を入力して下さい。
$cf{my_icon} = 0;

# 管理者専用アイコンの「ファイル名」を指定
$cf{my_gif}  = 'admin.gif';

# 返信がつくと親記事をトップへ移動 (0=no 1=yes)
$cf{topsort} = 1;

# ミニカウンタの設置
# → 0=no 1=テキスト 2=画像
$cf{counter} = 1;

# ミニカウンタの桁数
$cf{mini_fig} = 6;

# 記事 [タイトル] 部の長さ (全角文字換算)
$cf{sub_len} = 15;

# １ページ当たりの記事表示数 (親記事)
$cf{pg_max} = 10;

# 投稿があるとメール通知する (sendmail必須)
# 0 : 通知しない
# 1 : 通知する
$cf{mailing} = 0;

# メールアドレス(メール通知する時)
$cf{mailto} = 'xxx@xxx.xx';

# sendmailパス（メール通知する時）
$cf{sendmail} = '/usr/lib/sendmail';

# sendmailの -fコマンドが必要な場合
# 0=no 1=yes
$cf{sendm_f} = 0;

# 文字色の設定
# →　スペースで区切る
$cf{colors} = '#800000 #df0000 #008040 #0000ff #c100c1 #ff80c0 #ff8040 #000080 #808000';

# URLの自動リンク (0=no 1=yes)
$cf{autolink} = 1;

# ホスト取得方法
# 0 : gethostbyaddr関数を使わない
# 1 : gethostbyaddr関数を使う
$cf{gethostbyaddr} = 0;

# アクセス制限（半角スペースで区切る、アスタリスク可）
# → 拒否ホスト名を記述（後方一致）【例】*.anonymizer.com
$cf{deny_host} = '';
# → 拒否IPアドレスを記述（前方一致）【例】210.12.345.*
$cf{deny_addr} = '';

# １回当りの最大投稿サイズ (bytes)
$cf{maxdata} = 51200;

# 記事の更新は method=POST 限定する場合（セキュリティ対策）
# → 0=no 1=yes
$cf{postonly} = 1;

# 投稿制限（セキュリティ対策）
# 0 : しない
# 1 : 同一IPアドレスからの投稿間隔を制限する
# 2 : 全ての投稿間隔を制限する
$cf{regCtl} = 1;

# 制限投稿間隔（秒数）
# → $cf{regCtl} での投稿間隔
$cf{wait} = 60;

# 禁止ワード
# → コンマで区切って複数指定（例）$cf{no_word} = 'アダルト,出会い';
$cf{no_wd} = '';

# 日本語チェック（投稿時日本語が含まれていなければ拒否する）
# 0=No  1=Yes
$cf{jp_wd} = 1;

# URL個数チェック
# → 投稿コメント中に含まれるURL個数の最大値
$cf{urlnum} = 2;

# クッキーID名（特に変更しなくてよい）
$cf{cookie_id}  = "yyboard";  # フォーム入力
$cf{cookie_id3} = "yybpass";  # アクセス制限

# 管理パスワードの最大間違い制限
# → この回数以上パスワードを間違うとロックします
$cf{max_failpass} = 5;

# -------------------------------------------------------------- #
# [ 以下は「過去ログ」機能を使用する場合の設定 ]
#
# 過去ログ生成
# → 0=no 1=yes
$cf{pastkey} = 0;

# 過去ログ用NOファイル【サーバパス】
$cf{nofile}  = './data/pastno.dat';

# 過去ログのディレクトリ【サーバパス】
# → パスの最後に / をつけない
$cf{pastdir} = './data/past';

# 過去ログ１ファイルの行数
# → この行数を超えると次ページを自動生成します
$cf{pastmax} = 600;

# -------------------------------------------------------------- #
# [ 以下は「画像認証機能」機能を使用する場合の設定 ]
#
# 画像認証機能の使用
# 0 : しない
# 1 : ライブラリ版（pngren.pl）
# 2 : モジュール版（GD::SecurityImage + Image::Magick）→ Image::Magick必須
$cf{use_captcha} = 1;

# 認証用画像生成ファイル【URLパス】
$cf{captcha_cgi} = './captcha.cgi';

# 画像認証プログラム【サーバパス】
$cf{captcha_pl} = './lib/captcha.pl';
$cf{captsec_pl} = './lib/captsec.pl';
$cf{pngren_pl}  = './lib/pngren.pl';

# 画像認証機能用暗号化キー（暗号化/復号化をするためのキー）
# → 適当に変更してください。
$cf{captcha_key} = 'captyyboard';

# 投稿キー許容時間（分単位）
# → 投稿フォーム表示後、送信ボタンが押されるまでの可能時間。
$cf{cap_time} = 30;

# 投稿キーの文字数
# ライブラリ版 : 4～8文字で設定
# モジュール版 : 6～8文字で設定
$cf{cap_len} = 6;

# 画像/フォント格納ディレクトリ【サーバパス】
$cf{bin_dir} = './lib/bin';

# [ライブラリ版] 画像ファイル [ ファイル名のみ ]
$cf{si_png} = "stamp.png";

# [モジュール版] 画像フォント [ ファイル名のみ ]
$cf{font_ttl} = "tempest.ttf";

#===========================================================
# ■ 設定完了
#===========================================================

# アイコン追加
push(@{$cf{icon}},"$cf{my_gif},管理者用") if ($cf{my_icon});

# 設定内容を返す
sub set_init { return %cf; }

#-----------------------------------------------------------
#  フォームデコード
#-----------------------------------------------------------
sub parse_form {
	my ($buf,%in);
	if ($ENV{REQUEST_METHOD} eq "POST") {
		error('受理できません') if ($ENV{CONTENT_LENGTH} > $cf{maxdata});
		read(STDIN, $buf, $ENV{CONTENT_LENGTH});
	} else {
		$buf = $ENV{QUERY_STRING};
	}
	foreach ( split(/&/,$buf) ) {
		my ($key,$val) = split(/=/);
		$key =~ tr/+/ /;
		$key =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("H2", $1)/eg;
		$val =~ tr/+/ /;
		$val =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("H2", $1)/eg;
		
		# 無効化
		$key =~ s/[<>"'&\r\n]//g;
		$val =~ s/&/&amp;/g;
		$val =~ s/</&lt;/g;
		$val =~ s/>/&gt;/g;
		$val =~ s/"/&quot;/g;
		$val =~ s/'/&#39;/g;
		$val =~ s|\r\n|<br>|g;
		$val =~ s|[\r\n]|<br>|g;
		
		$in{$key} .= "\0" if (defined $in{$key});
		$in{$key} .= $val;
	}
	return %in;
}

#-----------------------------------------------------------
#  エラー画面
#-----------------------------------------------------------
sub error {
	my $err = shift;
	
	open(IN,"$cf{tmpldir}/error.html") or die;
	my $tmpl = join('',<IN>);
	close(IN);
	
	$tmpl =~ s/!error!/$err/g;
	$tmpl =~ s|!bbs_css!|$cf{cmnurl}/bbs.css|g;
	
	print "Content-type: text/html; charset=utf-8\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  パスワード制限
#-----------------------------------------------------------
sub passwd {
	my %in = @_;
	
	# 入室フォーム指定のとき
	if ($in{mode} eq 'enter') { pwd_form(); }
	
	# 時間取得
	my $now = time;
	
	# ログインのとき
	if ($in{login}) {
		# 認証
		if ($in{pw} ne $cf{enter_pwd}) { error("認証できません"); }
		
		# セッション発行
		my @wd = (0 .. 9, 'a' .. 'z', 'A' .. 'Z', '_');
		my $ses;
		for (1 .. 25) {	$ses .= $wd[int(rand(@wd))]; }
		
		# セッション更新
		my @log;
		open(DAT,"+< $cf{datadir}/ses.cgi");
		eval 'flock(DAT,2);';
		while(<DAT>) {
			chomp;
			my ($id,$time) = split(/\t/);
			next if ($now - $time > $cf{sestime} * 60);
			
			push(@log,"$_\n");
		}
		unshift(@log,"$ses\t$now\n");
		seek(DAT,0,0);
		print DAT @log;
		truncate(DAT,tell(DAT));
		close(DAT);
		
		# クッキー格納
		print "Set-Cookie: $cf{cookie_id3}=$ses\n";
	
	# セッション確認
	} else {
		
		# クッキー取得
		my $cook = $ENV{HTTP_COOKIE};
		
		# 該当IDを取り出す
		my %cook;
		foreach ( split(/;/, $cook) ) {
			my ($key,$val) = split(/=/);
			$key =~ s/\s//g;
			$cook{$key} = $val;
		}
		
		# クッキーなし
		if ($cook{$cf{cookie_id3}} eq '') { pwd_form(); }
		
		# ログオフのとき
		if ($in{mode} eq 'logoff') {
			
			my @log;
			open(DAT,"+< $cf{datadir}/ses.cgi");
			eval 'flock(DAT,2);';
			while(<DAT>) {
				my ($id,undef) = split(/\t/);
				next if ($cook{$cf{cookie_id3}} eq $id);
				
				push(@log,$_);
			}
			seek(DAT, 0, 0);
			print DAT @log;
			truncate(DAT, tell(DAT));
			close(DAT);
			
			if ($ENV{PERLXS} eq "PerlIS") {
				print "HTTP/1.0 302 Temporary Redirection\r\n";
				print "Content-type: text/html\n";
			}
			print "Set-Cookie: $cf{cookie_id3}=;\n";
			print "Location: $cf{homepage}\n\n";
			exit;
		}
		
		# セッションチェック
		my $flg;
		open(DAT,"$cf{datadir}/ses.cgi") or error("open err: ses.cgi");
		while(<DAT>) {
			chomp;
			my ($id,$time) = split(/\t/);
			
			if ($cook{$cf{cookie_id3}} eq $id) {
				# 時間オーバー
				if ($now - $time > $cf{sestime} * 60) {
					$flg = -1;
				# OK
				} else {
					$flg = 1;
				}
				last;
			}
		}
		close(DAT);
		
		# 時間オーバー
		if ($flg == -1) {
			my $msg = qq|入室時間が経過しました。再度ログインしてください<br>\n|;
			$msg .= qq|[<a href="$cf{bbs_cgi}?mode=enter">ログイン</a>]\n|;
			error($msg);
		
		# セッション情報なし
		} elsif (!$flg) {
			pwd_form();
		}
	}
}

#-----------------------------------------------------------
#  入室画面
#-----------------------------------------------------------
sub pwd_form {
	open(IN,"$cf{tmpldir}/enter.html") or error('open err: enter.html');
	my $tmpl = join('',<IN>);
	close(IN);
	
	$tmpl =~ s/!bbs_cgi!/$cf{bbs_cgi}/g;
	$tmpl =~ s|!bbs_css!|$cf{cmnurl}/bbs.css|g;
	
	print "Content-type: text/html; charset=utf-8\n\n";
	footer($tmpl);
}



1;

