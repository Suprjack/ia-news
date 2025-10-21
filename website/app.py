from flask import Flask, render_template, request, jsonify
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scraper.scraper import IANewsScraper

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-me'

# Configuration
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
NEWS_FILE = DATA_DIR / 'ia_news.json'

def load_news():
    """Load news from JSON file"""
    try:
        if NEWS_FILE.exists():
            with open(NEWS_FILE, 'r', encoding='utf-8') as f:
                news = json.load(f)
                # Sort by published_date (newest first)
                news.sort(key=lambda x: x.get('published_date', ''), reverse=True)
                return news
    except Exception as e:
        print(f"Error loading news: {e}")
    return []

@app.route('/')
def home():
    """Home page with all news"""
    news = load_news()

    # Count by category
    categories = {}
    for article in news:
        cat = article.get('category', 'general')
        categories[cat] = categories.get(cat, 0) + 1

    return render_template(
        'index.html',
        news=news,
        categories=categories,
        total_articles=len(news),
        last_updated=datetime.now().strftime("%d %B %Y à %H:%M")
    )

@app.route('/api/news')
def api_news():
    """API endpoint for news"""
    news = load_news()
    category = request.args.get('category', 'all')
    limit = request.args.get('limit', type=int, default=50)

    if category != 'all':
        news = [n for n in news if n.get('category') == category]

    return jsonify(news[:limit])

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    news = load_news()

    categories = {}
    sources = {}
    source_types = {}

    for article in news:
        cat = article.get('category', 'general')
        categories[cat] = categories.get(cat, 0) + 1

        src = article.get('source', 'Unknown')
        sources[src] = sources.get(src, 0) + 1

        stype = article.get('source_type', 'unknown')
        source_types[stype] = source_types.get(stype, 0) + 1

    return jsonify({
        'total_articles': len(news),
        'categories': categories,
        'sources': sources,
        'source_types': source_types,
        'last_updated': datetime.now().isoformat()
    })

@app.route('/refresh')
def refresh():
    """Manually trigger scraper"""
    try:
        scraper = IANewsScraper()
        count = scraper.run()
        return jsonify({
            'status': 'success',
            'message': f'Scraper executed successfully. {count} articles total.',
            'count': count
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/category/<category>')
def category(category):
    """Category page"""
    all_news = load_news()
    news = [n for n in all_news if n.get('category') == category]

    return render_template(
        'index.html',
        news=news,
        current_category=category,
        total_articles=len(news)
    )

@app.route('/search')
def search():
    """Search news"""
    query = request.args.get('q', '').lower()
    news = load_news()

    if query:
        news = [
            n for n in news
            if query in n.get('title', '').lower()
            or query in n.get('description', '').lower()
        ]

    return render_template(
        'index.html',
        news=news,
        search_query=query,
        total_articles=len(news)
    )

@app.route('/rss')
def rss():
    """RSS feed"""
    from datetime import datetime
    news = load_news()[:20]

    rss_content = '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>IA News - Actualités en Intelligence Artificielle</title>
        <link>http://localhost:8001</link>
        <description>Les dernières actualités en IA, LLMs, Image Generation, et plus.</description>
        <language>fr-fr</language>
        <lastBuildDate>{}</lastBuildDate>
'''.format(datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000"))

    for article in news:
        rss_content += '''
        <item>
            <title>{}</title>
            <link>{}</link>
            <description>{}</description>
            <pubDate>{}</pubDate>
            <category>{}</category>
            <source>{}</source>
        </item>
'''.format(
            article.get('title', '')[:100],
            article.get('url', ''),
            article.get('description', '')[:200],
            article.get('published_date', ''),
            article.get('category', 'general'),
            article.get('source', '')
        )

    rss_content += '''
    </channel>
</rss>
'''

    return rss_content, 200, {'Content-Type': 'application/rss+xml; charset=utf-8'}

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404

@app.context_processor
def inject_globals():
    """Inject global variables into templates"""
    return {
        'current_year': datetime.now().year,
        'app_name': 'IA News'
    }

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    DATA_DIR.mkdir(exist_ok=True)

    # Run the app
    print("\n" + "="*60)
    print("🚀 IA News Web Server")
    print("="*60)
    print("📍 http://localhost:8001")
    print("🔄 RSS: http://localhost:8001/rss")
    print("📊 API: http://localhost:8001/api/news")
    print("="*60 + "\n")

    app.run(
        host='0.0.0.0',
        port=8001,
        debug=True,
        use_reloader=True
    )
