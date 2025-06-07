# 山口県よさこい連絡協議会 Webサイト

このプロジェクトは、山口県よさこい連絡協議会のWebサイトをCGIベースのシステムからNetlifyで動作する静的サイトに移行するためのものです。

## 概要

古いCGIベースの新着情報システムを、最新のJavaScriptとNetlify CMSを使った静的サイトに変換します。これにより：

- サーバー依存のCGIスクリプトが不要になる
- Netlifyでの無料ホスティングが可能になる
- モダンな管理インターフェースが使える
- モバイル対応のレスポンシブデザイン
- セキュリティの向上

## セットアップ手順

### 1. 環境準備

```bash
# 必要なパッケージをインストール
npm install
```

### 2. データ変換

古いデータを新しいJSONフォーマットに変換します：

```bash
# データ変換スクリプトを実行
npm run convert
```

### 3. 画像ファイルの移行

img_cgiフォルダの画像ファイルをimagesフォルダにコピーします：

```bash
# Windowsの場合
xcopy /E /I img_cgi images

# macOS/Linuxの場合
cp -R img_cgi/* images/
```

### 4. ローカルでの確認

```bash
# 開発サーバーを起動
npm start
```

ブラウザで http://localhost:8080 にアクセスして確認できます。

### 5. Netlifyへのデプロイ

1. GitHubにリポジトリを作成してプッシュします
2. Netlifyにサインインし、「New site from Git」を選択
3. GitHubのリポジトリを選択
4. ビルド設定はデフォルトのままで大丈夫です
5. 「Deploy site」をクリック

### 6. Netlify CMSの設定

1. Netlifyのサイト管理画面で「Site settings」→「Identity」を選択
2. 「Enable Identity」をクリック
3. 「Settings and usage」で「Registration」を「Invite only」に設定
4. 「Services」→「Git Gateway」を有効化
5. 管理者ユーザーを招待（「Invite users」ボタン）

## ファイル構成

- `index.html` - メインページ
- `app.js` - 新着情報を表示するJavaScriptアプリケーション
- `new-style.css` - 新しいスタイルシート
- `converter.js` - 古いデータを変換するためのスクリプト
- `data/topics.json` - 新着情報のJSONデータ
- `admin/` - Netlify CMS関連ファイル
- `images/` - 画像ファイル

## 管理方法

サイトがデプロイされたら、`https://あなたのサイト.netlify.app/admin/` にアクセスして管理画面にログインできます。

ここから新着情報の追加・編集・削除が可能です。

## 注意点

1. 古いCGIシステムとの互換性を保つために、data/topics.datのバックアップを取っておくことをおすすめします。
2. サイトマップや検索エンジン向けの設定は必要に応じて追加してください。
3. HTMLタグを含む投稿を作成する場合は、「HTMLを使用」オプションをオンにしてください。
