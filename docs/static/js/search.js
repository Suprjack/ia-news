/**
 * Advanced search functionality for AI News
 * Real-time search with filters
 */

class SearchEngine {
    constructor() {
        this.articles = [];
        this.searchResults = [];
        this.filters = {
            category: 'all',
            source: 'all',
            query: ''
        };
        this.isOpen = false;
        this.init();
    }

    init() {
        // Extract articles from DOM
        this.extractArticles();

        // Setup search elements
        this.setupSearchUI();

        // Listen for language changes
        window.addEventListener('languageChanged', () => {
            this.updateSearchUI();
        });

        // Keyboard shortcut: Ctrl/Cmd + K
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                this.openSearch();
            }
        });
    }

    /**
     * Extract all articles from the DOM
     */
    extractArticles() {
        this.articles = [];
        document.querySelectorAll('.news-card, .archive-article').forEach(card => {
            const title = card.querySelector('.card-title, .article-title')?.textContent || '';
            const description = card.querySelector('.card-description')?.textContent || '';
            const source = card.querySelector('.card-source, .article-source')?.textContent || '';
            const category = card.getAttribute('data-category') || 'general';
            const url = card.querySelector('a')?.href || '';
            const date = card.querySelector('.card-date, .article-date')?.textContent || '';

            this.articles.push({
                title: title.trim(),
                description: description.trim(),
                source: source.trim(),
                category: category,
                url: url,
                date: date.trim(),
                element: card
            });
        });
    }

    /**
     * Setup search UI elements
     */
    setupSearchUI() {
        // Create search overlay if not exists
        if (!document.getElementById('searchOverlay')) {
            const overlay = document.createElement('div');
            overlay.id = 'searchOverlay';
            overlay.className = 'search-overlay';
            overlay.innerHTML = `
                <div class="search-modal">
                    <div class="search-header">
                        <input
                            type="text"
                            id="searchInput"
                            class="search-input"
                            data-i18n-placeholder="search.filter_by_source"
                            autocomplete="off"
                        >
                        <button class="search-close" onclick="searchEngine.closeSearch()">&times;</button>
                    </div>
                    <div class="search-filters">
                        <select id="categoryFilter" class="search-filter-select">
                            <option value="all" data-i18n-value="filters.all_news">Toutes les catégories</option>
                            <option value="llms">LLMs</option>
                            <option value="creative">Créatif</option>
                            <option value="nocode">No-Code</option>
                            <option value="hardware">Hardware</option>
                            <option value="general">Général</option>
                        </select>
                    </div>
                    <div id="searchResults" class="search-results"></div>
                </div>
            `;
            document.body.appendChild(overlay);

            // Close on background click
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    this.closeSearch();
                }
            });

            // Setup search input
            const input = document.getElementById('searchInput');
            input.addEventListener('input', () => this.performSearch());

            // Setup category filter
            const categoryFilter = document.getElementById('categoryFilter');
            categoryFilter.addEventListener('change', () => this.performSearch());

            // Close on Escape
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.isOpen) {
                    this.closeSearch();
                }
            });
        }

        // Create search button in navbar
        if (!document.getElementById('searchBtn')) {
            const navActions = document.querySelector('.nav-actions');
            if (navActions) {
                const searchBtn = document.createElement('button');
                searchBtn.id = 'searchBtn';
                searchBtn.className = 'search-btn';
                searchBtn.innerHTML = '<i class="fas fa-search"></i>';
                searchBtn.setAttribute('data-i18n-title', 'search.filter_by_source');
                searchBtn.onclick = () => this.openSearch();
                navActions.insertBefore(searchBtn, navActions.firstChild);
            }
        }
    }

    /**
     * Perform search with current filters
     */
    performSearch() {
        const searchInput = document.getElementById('searchInput');
        const categoryFilter = document.getElementById('categoryFilter');

        const query = (searchInput?.value || '').toLowerCase();
        const category = categoryFilter?.value || 'all';

        this.filters.query = query;
        this.filters.category = category;

        // Filter articles
        this.searchResults = this.articles.filter(article => {
            const matchesQuery = !query ||
                article.title.toLowerCase().includes(query) ||
                article.description.toLowerCase().includes(query) ||
                article.source.toLowerCase().includes(query);

            const matchesCategory = category === 'all' || article.category === category;

            return matchesQuery && matchesCategory;
        });

        this.displayResults();
    }

    /**
     * Display search results
     */
    displayResults() {
        const resultsContainer = document.getElementById('searchResults');
        if (!resultsContainer) return;

        const query = this.filters.query;

        if (!query && this.filters.category === 'all') {
            resultsContainer.innerHTML = `
                <div class="search-hint">
                    <i class="fas fa-search"></i>
                    <p>${i18n.t('search.filter_by_source')}</p>
                </div>
            `;
            return;
        }

        if (this.searchResults.length === 0) {
            resultsContainer.innerHTML = `
                <div class="search-empty">
                    <i class="fas fa-inbox"></i>
                    <h3>${i18n.t('search.no_results')}</h3>
                    <p>${i18n.t('search.try_different')}</p>
                </div>
            `;
            return;
        }

        const resultCount = this.searchResults.length;
        const countText = resultCount === 1
            ? i18n.t('search.found', { count: resultCount })
            : i18n.t('search.found_plural', { count: resultCount });

        let html = `<div class="search-count">${countText}</div>`;

        this.searchResults.forEach(article => {
            const highlightedTitle = this.highlightQuery(article.title, query);
            const highlightedDesc = this.highlightQuery(article.description.substring(0, 100), query);

            html += `
                <a href="${article.url}" class="search-result-item" target="_blank" rel="noopener">
                    <div class="result-title">${highlightedTitle}</div>
                    <div class="result-desc">${highlightedDesc}...</div>
                    <div class="result-meta">
                        <span class="result-source"><i class="fas fa-rss"></i> ${article.source}</span>
                        <span class="result-category">${article.category}</span>
                    </div>
                </a>
            `;
        });

        resultsContainer.innerHTML = html;
    }

    /**
     * Highlight query matches in text
     */
    highlightQuery(text, query) {
        if (!query) return text;
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    /**
     * Open search
     */
    openSearch() {
        const overlay = document.getElementById('searchOverlay');
        if (overlay) {
            overlay.classList.add('active');
            this.isOpen = true;
            document.getElementById('searchInput')?.focus();
        }
    }

    /**
     * Close search
     */
    closeSearch() {
        const overlay = document.getElementById('searchOverlay');
        if (overlay) {
            overlay.classList.remove('active');
            this.isOpen = false;
            document.getElementById('searchInput').value = '';
            this.filters.query = '';
            this.filters.category = 'all';
            document.getElementById('categoryFilter').value = 'all';
        }
    }

    /**
     * Update search UI after language change
     */
    updateSearchUI() {
        if (i18n) {
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.placeholder = i18n.t('search.filter_by_source');
            }
        }
        this.performSearch();
    }
}

// Initialize search globally when DOM is ready
let searchEngine;
document.addEventListener('DOMContentLoaded', () => {
    searchEngine = new SearchEngine();
});
