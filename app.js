/**
 * 山口県よさこい連絡協議会の新着情報表示スクリプト
 * Netlify対応版
 */

// ニュースアプリケーション
class NewsApp {
  constructor() {
    this.newsData = [];
    this.filteredData = [];
    this.currentPage = 1;
    this.itemsPerPage = 5;
    this.searchKeywords = [];
    this.searchCondition = 0; // 0: OR, 1: AND
    
    this.init();
  }

  async init() {
    await this.loadNewsData();
    this.setupEventListeners();
    this.displayNews();
    this.updatePagination();
  }

  async loadNewsData() {
    const loadingElement = document.getElementById('loading-message');
    const containerElement = document.getElementById('news-container');
    
    try {
      loadingElement.style.display = 'block';
      loadingElement.textContent = 'データを読み込み中...';
      
      // まず既存のJSONファイルから読み込み（フォールバック）
      let response = await fetch('./data/topics.json');
      
      // Netlify Functionsが利用可能な場合はそちらを使用
      if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
        try {
          const functionsResponse = await fetch('/.netlify/functions/fetch-news');
          if (functionsResponse.ok) {
            response = functionsResponse;
          }
        } catch (functionsError) {
          console.log('Netlify Functions利用不可、JSONファイルを使用:', functionsError);
        }
      }
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      this.newsData = await response.json();
      this.filteredData = [...this.newsData];
      
      loadingElement.style.display = 'none';
      containerElement.style.display = 'block';
      
    } catch (error) {
      console.error('ニュースデータの読み込みエラー:', error);
      loadingElement.textContent = 'データの読み込みに失敗しました。しばらくしてから再度お試しください。';
      
      // エラー時は既存のサンプルデータを表示
      this.newsData = this.getSampleData();
      this.filteredData = [...this.newsData];
      
      setTimeout(() => {
        loadingElement.style.display = 'none';
        containerElement.style.display = 'block';
        this.displayNews();
        this.updatePagination();
      }, 2000);
    }
  }

  getSampleData() {
    return [
      {
        id: 1,
        date: "2025/06/10 10:00:00",
        title: "Google Formsシステム導入のお知らせ",
        content: "新着情報の投稿がより簡単になりました。\n\n管理者の方は専用のGoogleフォームから記事を投稿できます。\n投稿後は自動的にサイトに反映されます。",
        images: [],
        useHtml: false,
        isYoutube: false,
        youtube: "",
        category: "お知らせ",
        priority: "高"
      }
    ];
  }

  setupEventListeners() {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const searchCondition = document.getElementById('search-condition');
    const resetButton = document.getElementById('reset-search');

    if (searchForm) {
      searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        this.handleSearch();
      });
    }

    if (resetButton) {
      resetButton.addEventListener('click', () => {
        this.resetSearch();
      });
    }

    if (searchInput) {
      searchInput.addEventListener('input', () => {
        if (searchInput.value.trim() === '') {
          this.resetSearch();
        }
      });
    }

    if (searchCondition) {
      searchCondition.addEventListener('change', () => {
        if (this.searchKeywords.length > 0) {
          this.handleSearch();
        }
      });
    }
  }

  handleSearch() {
    const searchInput = document.getElementById('search-input');
    const searchCondition = document.getElementById('search-condition');
    
    if (!searchInput || !searchCondition) return;

    const query = searchInput.value.trim();
    if (query === '') {
      this.resetSearch();
      return;
    }

    this.searchKeywords = query.split(/\s+/);
    this.searchCondition = parseInt(searchCondition.value);
    this.filterNews();
    this.currentPage = 1;
    this.displayNews();
    this.updatePagination();
  }

  resetSearch() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
      searchInput.value = '';
    }
    
    this.searchKeywords = [];
    this.filteredData = [...this.newsData];
    this.currentPage = 1;
    this.displayNews();
    this.updatePagination();
  }

  filterNews() {
    if (this.searchKeywords.length === 0) {
      this.filteredData = [...this.newsData];
      return;
    }

    this.filteredData = this.newsData.filter(item => {
      const searchText = `${item.title} ${item.content}`.toLowerCase();
      
      if (this.searchCondition === 1) { // AND検索
        return this.searchKeywords.every(keyword => 
          searchText.includes(keyword.toLowerCase())
        );
      } else { // OR検索
        return this.searchKeywords.some(keyword => 
          searchText.includes(keyword.toLowerCase())
        );
      }
    });
  }

  displayNews() {
    const container = document.getElementById('news-container');
    if (!container) return;

    const startIndex = (this.currentPage - 1) * this.itemsPerPage;
    const endIndex = startIndex + this.itemsPerPage;
    const pageData = this.filteredData.slice(startIndex, endIndex);

    if (pageData.length === 0) {
      container.innerHTML = '<p>該当する記事が見つかりませんでした。</p>';
      return;
    }

    container.innerHTML = pageData.map(item => this.createNewsItemHTML(item)).join('');
  }

  createNewsItemHTML(item) {
    const priorityClass = item.priority === '高' ? 'priority-high' : 
                         item.priority === '低' ? 'priority-low' : 'priority-medium';
    
    let contentHTML = item.content.replace(/\n/g, '<br>');
    
    // YouTubeコンテンツの処理
    if (item.isYoutube && item.youtube) {
      contentHTML += `<div class="youtube-container">${item.youtube}</div>`;
    }
    
    // 画像の処理
    let imagesHTML = '';
    if (item.images && item.images.length > 0) {
      imagesHTML = item.images.map(img => 
        `<img src="${img.path}" alt="画像" width="${img.width || 400}" height="${img.height || 300}" style="max-width: 100%; height: auto; margin: 10px 0;">`
      ).join('');
    }

    return `
      <div class="news-item ${priorityClass}">
        <div class="news-header">
          <h4>${item.title}</h4>
          <div class="news-meta">
            <span class="news-date">${item.date}</span>
            <span class="news-category">${item.category}</span>
            <span class="news-priority">${item.priority}</span>
          </div>
        </div>
        <div class="news-content">
          ${contentHTML}
          ${imagesHTML}
        </div>
      </div>
    `;
  }

  updatePagination() {
    const totalPages = Math.ceil(this.filteredData.length / this.itemsPerPage);
    const paginationContainer = document.querySelector('.pagination-controls');
    
    if (!paginationContainer) return;

    if (totalPages <= 1) {
      paginationContainer.innerHTML = '';
      return;
    }

    let paginationHTML = '';
    
    // 前のページボタン
    if (this.currentPage > 1) {
      paginationHTML += `<button onclick="newsApp.goToPage(${this.currentPage - 1})">前のページ</button>`;
    }
    
    // ページ番号
    for (let i = 1; i <= totalPages; i++) {
      const activeClass = i === this.currentPage ? 'active' : '';
      paginationHTML += `<button class="${activeClass}" onclick="newsApp.goToPage(${i})">${i}</button>`;
    }
    
    // 次のページボタン
    if (this.currentPage < totalPages) {
      paginationHTML += `<button onclick="newsApp.goToPage(${this.currentPage + 1})">次のページ</button>`;
    }
    
    paginationContainer.innerHTML = paginationHTML;
  }

  goToPage(page) {
    const totalPages = Math.ceil(this.filteredData.length / this.itemsPerPage);
    if (page >= 1 && page <= totalPages) {
      this.currentPage = page;
      this.displayNews();
      this.updatePagination();
    }
  }
}

// アプリケーション初期化
let newsApp;
document.addEventListener('DOMContentLoaded', () => {
  newsApp = new NewsApp();
});
