/**
 * 山口県よさこい連絡協議会の新着情報表示スクリプト
 * Markdownファイル対応版
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
    this.setupEventListeners();
    await this.loadNewsData();
    // displayNews()とupdatePagination()はloadNewsData()内で実行される
  }

  async loadNewsData() {
    const loadingElement = document.getElementById('loading-message');
    const containerElement = document.getElementById('news-container');
    const mainElement = document.getElementById('main');
    
    try {
      // ローディング状態に設定
      mainElement.classList.add('loading-state');
      containerElement.classList.remove('show');
      loadingElement.textContent = 'データを読み込み中...';
      
      // Markdownファイルから新着情報を読み込み
      this.newsData = await this.loadMarkdownPosts();
      this.filteredData = [...this.newsData];
      
      // データが読み込まれてからコンテンツを表示
      this.displayNews();
      this.updatePagination();
      
      // スムーズに表示を切り替え
      setTimeout(() => {
        mainElement.classList.remove('loading-state');
        document.getElementById('loading-message').style.display = 'none';
        containerElement.style.display = 'block';
        setTimeout(() => {
          containerElement.classList.add('show');
        }, 50);
      }, 300);
      
    } catch (error) {
      console.error('ニュースデータの読み込みエラー:', error);
      loadingElement.textContent = 'データの読み込みに失敗しました。しばらくしてから再度お試しください。';
      
      // エラー時は既存のサンプルデータを表示
      this.newsData = this.getSampleData();
      this.filteredData = [...this.newsData];
      
      setTimeout(() => {
        this.displayNews();
        this.updatePagination();
        mainElement.classList.remove('loading-state');
        containerElement.style.display = 'block';
        setTimeout(() => {
          containerElement.classList.add('show');
        }, 50);
      }, 1000);
    }
  }

  async loadMarkdownPosts() {
    try {
      // まず、ビルド済みのJSONファイルから読み込み
      const response = await fetch('./data/topics.json');
      if (response.ok) {
        return await response.json();
      }
    } catch (error) {
      console.log('JSONファイルから読み込み失敗、Markdownファイルから直接読み込みます');
    }

    // JSONファイルが利用できない場合は、Markdownファイルから直接読み込み
    return await this.loadMarkdownFilesDirectly();
  }

  async loadMarkdownFilesDirectly() {
    const posts = [];
    
    try {
      // まず、posts-list.jsonからファイル一覧を取得
      const listResponse = await fetch('./posts-list.json');
      let markdownFiles = [];
      
      if (listResponse.ok) {
        const fileList = await listResponse.json();
        markdownFiles = fileList.map(file => file.filename);
      } else {
        // フォールバック：既知のファイル一覧
        markdownFiles = [
          '2025-06-10-sample-post-1.md',
          '2025-06-08-event-announcement.md',
          '2025-06-07-youtube-video.md'
        ];
      }

      let id = 1;
      for (const filename of markdownFiles.sort().reverse()) {
        try {
          const response = await fetch(`_posts/${filename}`);
          if (response.ok) {
            const content = await response.text();
            const post = this.parseMarkdownFile(content, id++);
            if (post) {
              posts.push(post);
            }
          }
        } catch (error) {
          console.warn(`Markdownファイル ${filename} の読み込みに失敗:`, error);
        }
      }
    } catch (error) {
      console.error('ファイル一覧の取得に失敗:', error);
    }

    return posts;
  }

  parseMarkdownFile(content, id) {
    try {
      // フロントマターの抽出
      const frontmatterMatch = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
      
      if (!frontmatterMatch) {
        throw new Error('Invalid frontmatter format');
      }
      
      const frontmatterText = frontmatterMatch[1];
      const body = frontmatterMatch[2].trim();
      
      // 簡易YAMLパーサー（基本的なキー:値のペアのみ対応）
      const frontmatter = this.parseSimpleYaml(frontmatterText);
      
      // 画像の処理
      const images = frontmatter.images || [];
      const processedImages = Array.isArray(images) ? images.map(img => ({
        path: typeof img === 'string' ? img : img.path,
        width: typeof img === 'object' ? (img.width || 400) : 400,
        height: typeof img === 'object' ? (img.height || 300) : 300
      })) : [];
      
      // 日付の形式変換
      const date = new Date(frontmatter.date || Date.now());
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
      let processedContent;
      if (frontmatter.useHtml) {
        processedContent = this.markdownToHtml(body);
      } else {
        processedContent = this.markdownToText(body);
      }
      
      return {
        id: id,
        date: formattedDate,
        title: frontmatter.title || 'タイトルなし',
        content: processedContent,
        images: processedImages,
        useHtml: frontmatter.useHtml || false,
        isYoutube: !!frontmatter.youtube,
        youtube: frontmatter.youtube || '',
        category: frontmatter.category || 'お知らせ',
        priority: frontmatter.priority || '中'
      };
      
    } catch (error) {
      console.error('Markdownファイルの解析エラー:', error);
      return null;
    }
  }

  parseSimpleYaml(yamlText) {
    const result = {};
    const lines = yamlText.split('\n');
    let currentKey = null;
    let currentArray = null;
    
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed) continue;
      
      // 配列の要素
      if (trimmed.startsWith('- ')) {
        if (currentArray && currentKey) {
          const value = trimmed.substring(2).trim();
          if (value.includes(':')) {
            // オブジェクトの場合
            const obj = {};
            const parts = value.split(',');
            for (const part of parts) {
              const [k, v] = part.split(':').map(s => s.trim());
              if (k && v) {
                obj[k] = isNaN(v) ? v : parseInt(v);
              }
            }
            currentArray.push(obj);
          } else {
            currentArray.push(value);
          }
        }
        continue;
      }
      
      // キー:値のペア
      const colonIndex = trimmed.indexOf(':');
      if (colonIndex > 0) {
        const key = trimmed.substring(0, colonIndex).trim();
        const value = trimmed.substring(colonIndex + 1).trim();
        
        if (value === '') {
          // 配列の開始
          currentKey = key;
          currentArray = [];
          result[key] = currentArray;
        } else {
          // 通常の値
          currentKey = null;
          currentArray = null;
          
          // 型変換
          if (value === 'true') {
            result[key] = true;
          } else if (value === 'false') {
            result[key] = false;
          } else if (!isNaN(value) && value !== '') {
            result[key] = parseInt(value);
          } else {
            // 引用符を除去
            result[key] = value.replace(/^["']|["']$/g, '');
          }
        }
      }
    }
    
    return result;
  }

  markdownToText(markdown) {
    return markdown
      .replace(/^#+\s+/gm, '') // ヘッダー記号を削除
      .replace(/\*\*(.*?)\*\*/g, '$1') // 太字を削除
      .replace(/\*(.*?)\*/g, '$1') // 斜体を削除
      .replace(/\[(.*?)\]\(.*?\)/g, '$1') // リンクをテキストのみに
      .replace(/`(.*?)`/g, '$1') // インラインコードを削除
      .replace(/\n{2,}/g, '\n\n') // 複数の改行を調整
      .trim();
  }

  markdownToHtml(markdown) {
    return markdown
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2">$1</a>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/\n\n/g, '</p><p>')
      .replace(/\n/g, '<br>')
      .replace(/^(.*)$/, '<p>$1</p>');
  }

  getSampleData() {
    return [
      {
        id: 1,
        date: "2025/06/10 10:00:00",
        title: "Markdownファイルシステム導入のお知らせ",
        content: "新着情報の更新がより簡単になりました。\n\n_postsディレクトリ内にMarkdownファイルを追加するだけで、自動的にサイトに反映されます。\n\nファイル名は「YYYY-MM-DD-タイトル.md」の形式で作成してください。",
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

    // コンテンツ更新時のちらつきを防ぐ
    container.style.opacity = '0';
    
    setTimeout(() => {
      if (pageData.length === 0) {
        container.innerHTML = '<p>該当する記事が見つかりませんでした。</p>';
      } else {
        container.innerHTML = pageData.map(item => this.createNewsItemHTML(item)).join('');
      }
      
      // フェードインで表示
      container.style.opacity = '1';
    }, 100);
  }

  createNewsItemHTML(item) {
    const priorityClass = item.priority === '高' ? 'priority-high' : 
                         item.priority === '低' ? 'priority-low' : 'priority-medium';
    
    let contentHTML;
    if (item.useHtml) {
      // HTMLが有効な場合は、既にHTML変換済みのcontentをそのまま使用
      contentHTML = item.content.replace(/\r\n/g, '\n').replace(/\n/g, '<br>');
    } else {
      // HTMLが無効な場合は、改行のみ変換
      contentHTML = item.content.replace(/\n/g, '<br>');
    }
    
    // YouTubeコンテンツの処理
    if (item.isYoutube && item.youtube) {
      contentHTML += `<div class="youtube-container">${item.youtube}</div>`;
    }
    
    // 画像の処理
    let imagesHTML = '';
    if (item.images && item.images.length > 0) {
      imagesHTML = item.images.map(img => {
        const imagePath = img.path.startsWith('/') ? img.path : `/images/${img.path}`;
        return `<img src="${imagePath}" alt="画像" width="${img.width || 400}" height="${img.height || 300}" style="max-width: 100%; height: auto; margin: 10px 0;">`;
      }).join('');
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
