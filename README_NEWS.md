# 新着情報の更新方法

山口県よさこい連絡協議会のWebサイトの新着情報は、`_posts`ディレクトリ内のMarkdownファイルで管理されています。

## 新着情報を追加する方法

### 1. 新しいMarkdownファイルを作成

`_posts`ディレクトリ内に新しい`.md`ファイルを作成します。

**ファイル名の規則：**
```
YYYY-MM-DD-タイトル.md
```

例：`2025-06-15-spring-festival.md`

### 2. テンプレートを使用

`_posts/template.md`をコピーして、以下の内容を編集してください：

```markdown
---
title: "イベントのタイトル"
date: "2025-06-15 14:00:00"
category: "イベント"
priority: "高"
useHtml: false
images:
  - path: /images/event-photo.jpg
    width: 400
    height: 300
youtube: ""
---

ここに新着情報の内容を記述します。

## 詳細情報

Markdownの記法が使用できます。
```

### 3. フロントマターの設定項目

| 項目 | 説明 | 例 |
|------|------|-----|
| `title` | 記事のタイトル | "春の大会開催のお知らせ" |
| `date` | 投稿日時 | "2025-06-15 14:00:00" |
| `category` | カテゴリ | "お知らせ", "イベント", "結果" |
| `priority` | 優先度 | "高", "中", "低" |
| `useHtml` | HTML使用可否 | true / false |
| `images` | 画像情報 | 配列形式で指定 |
| `youtube` | YouTube埋め込みコード | iframe要素など |

### 4. 画像の追加方法

1. 画像ファイルを`images`ディレクトリに配置
2. フロントマターのimagesセクションに画像情報を追加：

```yaml
images:
  - path: /images/your-image.jpg
    width: 600
    height: 400
  - path: /images/another-image.png
    width: 300
    height: 200
```

### 5. YouTubeの埋め込み

YouTubeの埋め込みコードをyoutubeフィールドに記述：

```yaml
youtube: '<iframe width="560" height="315" src="https://www.youtube.com/embed/VIDEO_ID" frameborder="0" allowfullscreen></iframe>'
```

## ファイルの更新・削除

### 更新
既存のMarkdownファイルを編集して保存するだけで、サイトに反映されます。

### 削除
不要になった記事は、対応するMarkdownファイルを削除してください。

## ビルドコマンド

### 開発環境での確認
```bash
# ファイル一覧を更新
npm run list-posts

# JSONデータを生成
npm run build

# 全てのデータを更新
npm run build-all
```

### 本番環境
ファイルをアップロードするだけで自動的に反映されます。

## 注意事項

1. **ファイル名の形式を守る**: `YYYY-MM-DD-title.md`
2. **フロントマターの記述**: `---`で囲むYAML形式
3. **文字エンコーディング**: UTF-8で保存
4. **画像パス**: `/images/`から始まる絶対パス

## トラブルシューティング

### 新着情報が表示されない場合
1. ファイル名の形式を確認
2. フロントマターの記述を確認
3. 文字エンコーディングを確認
4. ブラウザのキャッシュをクリア

### 画像が表示されない場合
1. 画像ファイルが正しく配置されているか確認
2. パスの記述が正しいか確認
3. ファイル名に日本語や特殊文字が含まれていないか確認

お困りの際は、テンプレートファイルを参考にして作成してください。 