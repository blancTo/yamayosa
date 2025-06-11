/**
 * _postsディレクトリ内のMarkdownファイルを自動検出するスクリプト
 * フロントエンドでファイル一覧を取得するために使用
 */

const fs = require('fs');
const path = require('path');

// 設定
const POSTS_DIR = '_posts';
const OUTPUT_FILE = 'posts-list.json';

/**
 * Markdownファイルの一覧を生成
 */
function generatePostsList() {
  try {
    console.log('Markdownファイル一覧の生成を開始...');
    
    // 投稿ディレクトリの存在確認
    if (!fs.existsSync(POSTS_DIR)) {
      console.log(`投稿ディレクトリ ${POSTS_DIR} が見つかりません。`);
      // 空の配列を出力
      fs.writeFileSync(OUTPUT_FILE, JSON.stringify([], null, 2), 'utf-8');
      return;
    }
    
    // Markdownファイルの取得（template.mdを除外）
    const files = fs.readdirSync(POSTS_DIR)
      .filter(file => file.endsWith('.md') && file !== 'template.md')
      .sort()
      .reverse(); // 新しい順にソート
    
    console.log(`${files.length}件のMarkdownファイルを発見しました。`);
    
    // ファイル一覧の情報を取得
    const fileList = files.map(file => {
      const filepath = path.join(POSTS_DIR, file);
      const stats = fs.statSync(filepath);
      
      return {
        filename: file,
        path: `_posts/${file}`,
        lastModified: stats.mtime.toISOString(),
        size: stats.size
      };
    });
    
    // JSONファイルの出力
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(fileList, null, 2), 'utf-8');
    console.log(`✓ ${OUTPUT_FILE} に${fileList.length}件のファイル情報を出力しました。`);
    
  } catch (error) {
    console.error('ファイル一覧生成中にエラーが発生しました:', error.message);
    process.exit(1);
  }
}

// スクリプトが直接実行された場合
if (require.main === module) {
  generatePostsList();
}

module.exports = { generatePostsList }; 