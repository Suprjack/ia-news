/**
 * Article randomizer and mixer
 * Prevents repetitive article ordering (e.g., all OpenAI articles at the top)
 * Uses importance scoring based on source priority and recency
 */

class ArticleRandomizer {
    constructor() {
        // Priority scores for different sources (higher = more important)
        this.sourceScores = {
            'OpenAI Blog': 10,
            'Anthropic News': 10,
            'Google AI Blog': 9,
            'Hugging Face Blog': 8,
            'The Verge AI': 7,
            'TechCrunch AI': 7,
            'VentureBeat AI': 6,
            'MIT Technology Review AI': 6,
            'Ars Technica': 5,
            'Wired AI': 5,
            'AI News': 5,
            'NVIDIA Blog': 7,
            'Journal du Net - IA': 4,
            'Siècle Digital - IA': 4,
            'Maddyness - IA': 3,
            'PetaPixel - AI': 6,
            'RunwayML Blog': 6,
            'Webflow Blog': 3,
            'Bubble Blog': 3
        };

        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.mixArticles());
        } else {
            this.mixArticles();
        }
    }

    /**
     * Calculate importance score for an article
     */
    getArticleScore(article) {
        let score = 0;

        // Source priority
        const source = article.querySelector('.card-source')?.textContent?.trim() || '';
        const cleanSource = source.replace('📰 ', '').replace(/\s+/g, ' ').trim();
        score += this.sourceScores[cleanSource] || 3;

        // Recency bonus (newer = higher score)
        const dateElement = article.querySelector('.card-date');
        if (dateElement) {
            const dateText = dateElement.textContent.trim();
            const timeAgo = this.parseTimeAgo(dateText);
            if (timeAgo) {
                score += Math.max(5 - timeAgo, 0); // Bonus for very recent articles
            }
        }

        // Add small randomization to prevent strict ordering
        score += Math.random() * 2;

        return score;
    }

    /**
     * Parse relative time text (e.g., "2 hours ago" -> 2 hours)
     */
    parseTimeAgo(dateText) {
        const text = dateText.toLowerCase();

        if (text.includes('second')) {
            return 0;
        } else if (text.includes('minute')) {
            const num = parseInt(text);
            return num ? num / 60 : 1; // Convert to hours
        } else if (text.includes('hour')) {
            return parseInt(text) || 1;
        } else if (text.includes('day')) {
            return (parseInt(text) || 1) * 24; // Convert to hours
        }
        return null;
    }

    /**
     * Mix articles using importance scoring
     * Creates a balanced distribution instead of grouping by source
     */
    mixArticles() {
        const container = document.getElementById('newsGrid');
        if (!container) return;

        const articles = Array.from(container.querySelectorAll('.news-card:not(.trending-card)'));
        if (articles.length === 0) return;

        // Calculate scores and sort
        const articlesWithScores = articles.map(article => ({
            element: article,
            score: this.getArticleScore(article)
        }));

        // Sort by score (descending) for importance ranking
        articlesWithScores.sort((a, b) => b.score - a.score);

        // Create distribution that mixes high-importance articles with others
        const distributed = this.distributeArticles(articlesWithScores.map(a => a.element));

        // Reorder in DOM
        distributed.forEach((article, index) => {
            container.appendChild(article);
            // Add staggered animation
            article.style.opacity = '0';
            article.style.transform = 'translateY(10px)';

            setTimeout(() => {
                article.style.transition = 'opacity 0.4s ease-out, transform 0.4s ease-out';
                article.style.opacity = '1';
                article.style.transform = 'translateY(0)';
            }, index * 20);
        });
    }

    /**
     * Distribute articles to create balanced grid
     * Alternates between high-priority and lower-priority articles
     */
    distributeArticles(articles) {
        if (articles.length < 4) return articles;

        const distributed = [];
        const sorted = [...articles].sort((a, b) => {
            const scoreA = this.getArticleScore(a);
            const scoreB = this.getArticleScore(b);
            return scoreB - scoreA;
        });

        // Split into high and low priority
        const highPriority = sorted.slice(0, Math.ceil(sorted.length / 2));
        const lowPriority = sorted.slice(Math.ceil(sorted.length / 2));

        // Interleave: high, low, high, low, ...
        for (let i = 0; i < highPriority.length; i++) {
            distributed.push(highPriority[i]);
            if (lowPriority[i]) {
                distributed.push(lowPriority[i]);
            }
        }

        // Add remaining
        if (highPriority.length < lowPriority.length) {
            distributed.push(...lowPriority.slice(highPriority.length));
        }

        return distributed;
    }
}

// Initialize on DOM ready
const articleRandomizer = new ArticleRandomizer();
