/**
 * Markdownファイルから新着情報のJSONデータを生成するスクリプト
 * Netlify CMS対応版
 */

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

// 設定
const POSTS_DIR = '_posts';
const DATA_DIR = 'data';
const OUTPUT_FILE = path.join(DATA_DIR, 'topics.json');

/**
 * Markdownファイルのフロントマターとコンテンツを解析
 */
function parseMarkdownFile(filepath) {
  const content = fs.readFileSync(filepath, 'utf-8');
  
  // フロントマターの抽出（改行コードの違いに対応）
  const frontmatterMatch = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  
  if (!frontmatterMatch) {
    console.error(`File content preview:`, content.slice(0, 100));
    throw new Error(`Invalid frontmatter in file: ${filepath}`);
  }
  
  const frontmatter = yaml.load(frontmatterMatch[1]);
  const body = frontmatterMatch[2].trim();
  
  return { frontmatter, body };
}

/**
 * Markdownのbodyをプレーンテキストに変換（簡易版）
 */
function markdownToText(markdown) {
  return markdown
    .replace(/^#+\s+/gm, '') // ヘッダー記号を削除
    .replace(/\*\*(.*?)\*\*/g, '$1') // 太字を削除
    .replace(/\*(.*?)\*/g, '$1') // 斜体を削除
    .replace(/\[(.*?)\]\(.*?\)/g, '$1') // リンクをテキストのみに
    .replace(/`(.*?)`/g, '$1') // インラインコードを削除
    .replace(/\n{2,}/g, '\n\n') // 複数の改行を調整
    .trim();
}

/**
 * Markdownデータを旧形式のJSONに変換
 */
function convertToOldFormat(markdownData, index) {
  const { frontmatter, body } = markdownData;
  
  // 画像の処理
  const images = frontmatter.images || [];
  const processedImages = images.map(img => ({
    path: img.path.replace(/^\/images\//, ''), // /images/ プレフィックスを削除
    width: img.width || 400,
    height: img.height || 300
  }));
  
  // YouTubeの処理
  const isYoutube = !!frontmatter.youtube;
  const youtube = frontmatter.youtube || '';
  
  // 日付の形式変換
  const date = new Date(frontmatter.date);
  const formattedDate = date.toLocaleString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  }).replace(/\//g, '/');
  
  // 本文の処理
  let content;
  if (frontmatter.useHtml) {
    // HTMLを許可する場合はMarkdownをそのまま使用
    content = body;
  } else {
    // プレーンテキストに変換
    content = markdownToText(body);
  }
  
  return {
    id: index + 1,
    date: formattedDate,
    title: frontmatter.title,
    content: content,
    images: processedImages,
    useHtml: frontmatter.useHtml || false,
    isYoutube: isYoutube,
    youtube: youtube,
    category: frontmatter.category || 'お知らせ',
    priority: frontmatter.priority || '中'
  };
}

/**
 * メイン処理
 */
function buildPosts() {
  try {
    console.log('新着情報データの生成を開始...');
    
    // 投稿ディレクトリの存在確認
    if (!fs.existsSync(POSTS_DIR)) {
      console.log(`投稿ディレクトリ ${POSTS_DIR} が見つかりません。`);
      return;
    }
    
    // データディレクトリの作成
    if (!fs.existsSync(DATA_DIR)) {
      fs.mkdirSync(DATA_DIR, { recursive: true });
    }
    
    // Markdownファイルの取得（template.mdを除外）
    const files = fs.readdirSync(POSTS_DIR)
      .filter(file => file.endsWith('.md') && file !== 'template.md')
      .sort()
      .reverse(); // 新しい順にソート
    
    console.log(`${files.length}件の投稿ファイルを発見しました。`);
    
    // 各ファイルを処理
    const posts = [];
    files.forEach((file, index) => {
      try {
        const filepath = path.join(POSTS_DIR, file);
        console.log(`処理中: ${file}`);
        
        const markdownData = parseMarkdownFile(filepath);
        const post = convertToOldFormat(markdownData, index);
        posts.push(post);
        
      } catch (error) {
        console.error(`ファイル ${file} の処理中にエラーが発生しました:`, error.message);
      }
    });
    
    // JSONファイルの出力
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(posts, null, 2), 'utf-8');
    console.log(`✓ ${OUTPUT_FILE} に${posts.length}件の投稿データを出力しました。`);
    
  } catch (error) {
    console.error('ビルド処理中にエラーが発生しました:', error.message);
    process.exit(1);
  }
}

// スクリプトが直接実行された場合
if (require.main === module) {
  buildPosts();
}

module.exports = { buildPosts }; 