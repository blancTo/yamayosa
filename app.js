/**
 * 山口県よさこい連絡協議会の新着情報表示スクリプト
 * Netlify対応版
 */

// 設定
const CONFIG = {
  dataUrl: './data/topics.json',  // JSONデータの場所
  postsPerPage: 5,               // 1ページあたりの表示件数
  imageBaseUrl: './images/',     // 画像のベースURL
  defaultErrorImage: './img/notfound.jpg' // 画像エラー時の代替画像
};

// グローバル変数
let allPosts = [];        // すべての投稿データ
let currentPage = 0;      // 現在のページ
let filteredPosts = [];   // 検索でフィルタされた投稿データ
let isSearchActive = false; // 検索が有効かどうか

/**
 * アプリケーションの初期化
 */
document.addEventListener('DOMContentLoaded', () => {
  // データ読み込み
  fetchData();
  
  // 検索フォームのイベントリスナー設定
  document.getElementById('search-form').addEventListener('submit', (e) => {
    e.preventDefault();
    searchPosts();
  });
  
  // 検索リセットボタンのイベントリスナー設定
  document.getElementById('reset-search').addEventListener('click', () => {
    document.getElementById('search-input').value = '';
    isSearchActive = false;
    currentPage = 0;
    renderPosts(allPosts);
  });
});

/**
 * JSONデータを取得する
 */
async function fetchData() {
  try {
    const response = await fetch(CONFIG.dataUrl);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    allPosts = data;
    
    // 投稿をレンダリング（まだ非表示のまま）
    const newsContainer = document.getElementById('news-container');
    const loadingMessage = document.getElementById('loading-message');
    
    renderPosts(allPosts);
    
    // コンテンツの準備が完了したら即時表示（ちらつき防止）
    loadingMessage.style.display = 'none';
    newsContainer.style.display = 'block';
    newsContainer.classList.add('show');
    
  } catch (error) {
    console.error('データの読み込みに失敗しました:', error);
    document.getElementById('loading-message').textContent = 'データの読み込みに失敗しました。ページを再読み込みしてください。';
  }
}

/**
 * 投稿を表示する
 * @param {Array} posts - 表示する投稿の配列
 */
function renderPosts(posts) {
  // 投稿コンテナを取得
  const container = document.getElementById('news-container');
  container.innerHTML = '';
  
  // 現在のページの投稿のみを表示
  const startIndex = currentPage * CONFIG.postsPerPage;
  const endIndex = Math.min(startIndex + CONFIG.postsPerPage, posts.length);
  const currentPosts = posts.slice(startIndex, endIndex);
  
  if (currentPosts.length === 0) {
    container.innerHTML = '<p>表示する投稿がありません。</p>';
    document.querySelector('.pagination-controls').innerHTML = '';
    return;
  }
  
  // 各投稿をレンダリング
  currentPosts.forEach(post => {
    const postElement = createPostElement(post);
    container.appendChild(postElement);
  });
  
  // ページネーションを更新
  updatePagination(posts);
}

/**
 * 投稿要素を作成する
 * @param {Object} post - 投稿データ
 * @return {HTMLElement} - 投稿要素
 */
function createPostElement(post) {
  const article = document.createElement('div');
  article.className = 'news-item';
  
  // タイトルと日付のヘッダー
  const header = document.createElement('div');
  header.className = 'news-header';
  header.innerHTML = `
    <span class="news-icon">◇</span>
    <span class="news-title">${post.title}</span>
    <span class="news-date">${post.date}</span>
  `;
  
  // 本文
  const content = document.createElement('div');
  content.className = 'news-content';
  
  // 画像またはYouTube
  if (post.isYoutube && post.youtube) {
    const youtubeContainer = document.createElement('div');
    youtubeContainer.className = 'youtube-container';
    youtubeContainer.innerHTML = post.youtube;
    content.appendChild(youtubeContainer);
  } else if (post.images.length > 0) {
    const imageContainer = document.createElement('div');
    imageContainer.className = 'image-container';
    
    post.images.forEach(image => {
      const imgWrapper = document.createElement('div');
      imgWrapper.style.display = 'inline-block';
      imgWrapper.style.width = (image.width > CONFIG.postsPerPage ? CONFIG.postsPerPage : image.width) + 'px';
      imgWrapper.style.height = (image.height > CONFIG.postsPerPage ? CONFIG.postsPerPage : image.height) + 'px';
      imgWrapper.style.margin = '5px';
      imgWrapper.style.backgroundColor = '#f0f0f0';
      
      const img = document.createElement('img');
      img.width = image.width > CONFIG.postsPerPage ? CONFIG.postsPerPage : image.width;
      img.height = image.height > CONFIG.postsPerPage ? CONFIG.postsPerPage : image.height;
      img.className = 'news-image';
      img.alt = post.title;
      img.style.display = 'block';
      
      img.onload = function() {
        // 画像読み込み完了時の処理（必要であれば）
      };
      
      img.onerror = function() {
        this.src = CONFIG.defaultErrorImage;
        this.alt = '画像が見つかりません';
        this.style.opacity = '1';
      };
      
      // 画像をクリックで拡大表示
      img.addEventListener('click', () => {
        window.open(img.src, '_blank');
      });
      
      // 最後にsrcを設定して読み込み開始
      img.src = `${CONFIG.imageBaseUrl}${image.path}`;
      
      imgWrapper.appendChild(img);
      imageContainer.appendChild(imgWrapper);
    });
    
    content.appendChild(imageContainer);
  }
  
  // 本文テキスト
  const textContent = document.createElement('p');
  textContent.className = 'news-text';
  
  if (post.useHtml) {
    textContent.innerHTML = post.content;
  } else {
    textContent.innerHTML = post.content;
  }
  
  content.appendChild(textContent);
  
  // 記事に要素を追加
  article.appendChild(header);
  article.appendChild(content);
  
  return article;
}

/**
 * ページネーションを更新する
 * @param {Array} posts - 投稿の配列
 */
function updatePagination(posts) {
  const totalPages = Math.ceil(posts.length / CONFIG.postsPerPage);
  const paginationElement = document.querySelector('.pagination-controls');
  paginationElement.innerHTML = '';
  
  if (totalPages <= 1) {
    return;
  }
  
  // 「前へ」ボタン
  if (currentPage > 0) {
    const prevButton = document.createElement('button');
    prevButton.textContent = '前へ';
    prevButton.addEventListener('click', () => {
      currentPage--;
      renderPosts(posts);
      window.scrollTo(0, 0);
    });
    paginationElement.appendChild(prevButton);
  }
  
  // ページ番号
  const pageInfo = document.createElement('span');
  pageInfo.className = 'page-info';
  pageInfo.textContent = `${currentPage + 1} / ${totalPages}`;
  paginationElement.appendChild(pageInfo);
  
  // 「次へ」ボタン
  if (currentPage < totalPages - 1) {
    const nextButton = document.createElement('button');
    nextButton.textContent = '次へ';
    nextButton.addEventListener('click', () => {
      currentPage++;
      renderPosts(posts);
      window.scrollTo(0, 0);
    });
    paginationElement.appendChild(nextButton);
  }
  
  // ページ選択
  if (totalPages > 2) {
    const pageSelect = document.createElement('select');
    pageSelect.className = 'page-select';
    
    for (let i = 0; i < totalPages; i++) {
      const option = document.createElement('option');
      option.value = i;
      option.textContent = `${i + 1}ページ目`;
      if (i === currentPage) {
        option.selected = true;
      }
      pageSelect.appendChild(option);
    }
    
    pageSelect.addEventListener('change', (e) => {
      currentPage = parseInt(e.target.value);
      renderPosts(posts);
      window.scrollTo(0, 0);
    });
    
    paginationElement.appendChild(pageSelect);
  }
}

/**
 * 投稿を検索する
 */
function searchPosts() {
  const searchText = document.getElementById('search-input').value.trim();
  const condition = document.getElementById('search-condition').value;
  
  if (!searchText) {
    isSearchActive = false;
    currentPage = 0;
    renderPosts(allPosts);
    return;
  }
  
  isSearchActive = true;
  const keywords = searchText.split(/\s+/);
  
  filteredPosts = allPosts.filter(post => {
    // 検索対象のテキスト
    const searchTarget = `${post.title} ${post.content}`;
    
    if (condition === '1') {
      // AND検索
      return keywords.every(keyword => searchTarget.includes(keyword));
    } else {
      // OR検索
      return keywords.some(keyword => searchTarget.includes(keyword));
    }
  });
  
  currentPage = 0;
  renderPosts(filteredPosts);
}
