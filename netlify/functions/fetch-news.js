const { google } = require('googleapis');

exports.handler = async (event, context) => {
  // CORS設定
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Content-Type': 'application/json',
  };

  // プリフライトリクエストの処理
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: '',
    };
  }

  try {
    // 環境変数から設定を取得
    const serviceAccount = {
      type: 'service_account',
      project_id: process.env.GOOGLE_PROJECT_ID,
      private_key_id: process.env.GOOGLE_PRIVATE_KEY_ID,
      private_key: process.env.GOOGLE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
      client_email: process.env.GOOGLE_CLIENT_EMAIL,
      client_id: process.env.GOOGLE_CLIENT_ID,
      auth_uri: 'https://accounts.google.com/o/oauth2/auth',
      token_uri: 'https://oauth2.googleapis.com/token',
      auth_provider_x509_cert_url: 'https://www.googleapis.com/oauth2/v1/certs',
    };

    const SPREADSHEET_ID = process.env.GOOGLE_SPREADSHEET_ID;
    const RANGE = 'フォームの回答 1!A:E'; // A列:タイムスタンプ, B列:タイトル, C列:本文, D列:カテゴリ, E列:重要度

    // Google Sheets API認証
    const auth = new google.auth.GoogleAuth({
      credentials: serviceAccount,
      scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
    });

    const sheets = google.sheets({ version: 'v4', auth });

    // スプレッドシートからデータを取得
    const response = await sheets.spreadsheets.values.get({
      spreadsheetId: SPREADSHEET_ID,
      range: RANGE,
    });

    const rows = response.data.values || [];
    
    // ヘッダー行を除外
    const dataRows = rows.slice(1);

    // データをJSON形式に変換
    const newsData = dataRows.map((row, index) => {
      const [timestamp, title, content, category, priority] = row;
      
      return {
        id: index + 1,
        date: formatDate(timestamp),
        title: title || '無題',
        content: content || '',
        images: [],
        useHtml: false,
        isYoutube: false,
        youtube: '',
        category: category || 'お知らせ',
        priority: priority || '中'
      };
    }).reverse(); // 新しい順に並び替え

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify(newsData),
    };

  } catch (error) {
    console.error('Google Sheets API Error:', error);
    
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        error: 'データの取得に失敗しました',
        details: error.message 
      }),
    };
  }
};

// タイムスタンプを日本時間の文字列に変換
function formatDate(timestamp) {
  if (!timestamp) return new Date().toLocaleString('ja-JP');
  
  try {
    const date = new Date(timestamp);
    return date.toLocaleString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }).replace(/\//g, '/');
  } catch (error) {
    return new Date().toLocaleString('ja-JP');
  }
} 