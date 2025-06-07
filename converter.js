/**
 * topics.datをJSONに変換するスクリプト
 * 使用方法: node converter.js
 */

const fs = require('fs');
const path = require('path');
const iconv = require('iconv-lite'); // シフトJISの変換に必要

// 設定
const DATA_FILE = './data/topics.dat';
const JSON_OUTPUT = './data/topics.json';
const IMG_DIR = './img_cgi';
const NEW_IMG_DIR = './images';

// topics.datを読み込む
try {
  // シフトJISのファイルを読み込み、UTF-8に変換
  const buffer = fs.readFileSync(DATA_FILE);
  const content = iconv.decode(buffer, 'Shift_JIS');
  
  // 各行を処理
  const lines = content.split('\n').filter(line => line.trim());
  const posts = lines.map(line => {
    const [
      no, date, sub, com, 
      e1, w1, h1, 
      e2, w2, h2, 
      e3, w3, h3, 
      tag, clip, tube
    ] = line.split('<>');
    
    // 画像情報を整理
    const images = [];
    if (e1) {
      images.push({
        path: `${no}-1${e1}`,
        width: parseInt(w1, 10),
        height: parseInt(h1, 10)
      });
    }
    if (e2) {
      images.push({
        path: `${no}-2${e2}`,
        width: parseInt(w2, 10),
        height: parseInt(h2, 10)
      });
    }
    if (e3) {
      images.push({
        path: `${no}-3${e3}`,
        width: parseInt(w3, 10),
        height: parseInt(h3, 10)
      });
    }
    
    // JSONオブジェクトを作成
    return {
      id: parseInt(no, 10),
      date,
      title: sub,
      content: com,
      images,
      useHtml: tag === '1',
      isYoutube: clip === 't',
      youtube: tube || ''
    };
  });
  
  // 新しいJSONファイルを作成
  fs.writeFileSync(JSON_OUTPUT, JSON.stringify(posts, null, 2), 'utf8');
  console.log(`${posts.length}件のデータを${JSON_OUTPUT}に変換しました`);
  
  // 画像ディレクトリを作成
  if (!fs.existsSync(NEW_IMG_DIR)){
    fs.mkdirSync(NEW_IMG_DIR, { recursive: true });
  }
  
  // 画像をコピーする場合はここで処理
  console.log('画像のコピーはimagesディレクトリに手動で行ってください');
  
} catch (error) {
  console.error('エラーが発生しました:', error);
}
