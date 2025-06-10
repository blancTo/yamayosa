# Netlify CMS 安全なデプロイメントガイド

## 方法1: Netlify Identity を使用（推奨）

### 1. Netlifyへのデプロイ
```bash
# GitHubにプッシュ後、Netlifyでサイトを作成
```

### 2. Netlify Identity の設定
1. Netlify Dashboard → サイトを選択
2. Settings → Identity → Enable Identity
3. Settings → Identity → Registration → "Invite only" に設定
4. Settings → Identity → Services → Git Gateway → Enable Git Gateway

### 3. 管理者ユーザーの招待
1. Identity タブ → "Invite users"
2. 管理者のメールアドレスを入力
3. 管理者は招待メールからアカウント作成

### 4. 管理画面アクセス
- URL: `https://your-site.netlify.app/admin/`
- 管理者は自分専用のアカウントでログイン
- Netlifyアカウント全体にはアクセス不可

---

## 方法2: 専用Netlifyアカウント作成

### メリット
- 完全に分離された管理
- 管理者に全権限を渡せる

### 手順
1. 新しいメールアドレスでNetlifyアカウント作成
2. このプロジェクトを新アカウントでデプロイ
3. アカウント情報を管理者に渡す

---

## 方法3: GitHub連携のみ

### 設定変更
`admin/config.yml` を以下に変更：

```yaml
backend:
  name: github
  repo: your-username/yamayosa
  branch: main
```

### メリット
- GitHubアカウントのみで管理
- Netlifyアカウント不要

### 必要な権限
- GitHubリポジトリへの書き込み権限のみ

---

## セキュリティ上の注意事項

1. **Invite only** 設定を必ず使用
2. 管理者の退職時はアクセス権を即座に削除
3. 定期的にアクセスログを確認
4. 重要な変更は承認プロセスを設ける

## トラブルシューティング

### 管理画面にアクセスできない場合
1. Netlify Identity が有効化されているか確認
2. Git Gateway が有効化されているか確認
3. ユーザーが正しく招待されているか確認

### CMS で編集した内容が反映されない場合
1. ビルドログを確認
2. `build-posts.js` が正常に実行されているか確認
3. GitHubへのコミットが正常に行われているか確認 