import requests
import json
import re
import os
from datetime import datetime
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urlparse, urljoin
import feedparser
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IANewsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        self.news_file = os.path.join(self.data_dir, 'ia_news.json')

        # 🎯 SOURCES GRAND PUBLIC & ACCESSIBLES - FRANÇAISES & SYMPAS!
        self.sources = {
            'sites': [
                # 🎉 TRENDY & FUN
                {'url': 'https://www.producthunt.com/search?q=AI', 'category': 'fun', 'type': 'producthunt', 'name': 'Product Hunt'},

                # 🤖 GRANDS MODÈLES DE LANGAGE (LLM) - ACCESSIBLE
                {'url': 'https://www.popsci.com/technology/', 'category': 'llms', 'type': 'popsci', 'name': 'Popular Science'},
                {'url': 'https://www.techtarget.com/searchenterpriseai/', 'category': 'llms', 'type': 'techtarget', 'name': 'TechTarget'},
                {'url': 'https://huggingface.co/', 'category': 'llms', 'type': 'huggingface', 'name': 'HuggingFace'},
                {'url': 'https://openai.com/news', 'category': 'llms', 'type': 'openai', 'name': 'OpenAI'},

                # 🎨 GÉNÉRATEURS D'IMAGES IA
                {'url': 'https://zapier.com/blog/', 'category': 'image_gen', 'type': 'zapier', 'name': 'Zapier Magazine'},
                {'url': 'https://www.pcmag.com/news', 'category': 'image_gen', 'type': 'pcmag', 'name': 'PCMag'},
                {'url': 'https://www.reddit.com/r/StableDiffusion/', 'category': 'image_gen', 'type': 'reddit', 'name': 'Reddit Stable Diffusion'},
                {'url': 'https://www.reddit.com/r/Midjourney/', 'category': 'image_gen', 'type': 'reddit', 'name': 'Reddit Midjourney'},

                # 🎬 GÉNÉRATEURS VIDÉO IA
                {'url': 'https://www.nytimes.com/section/technology', 'category': 'video_gen', 'type': 'nytimes', 'name': 'New York Times - Tech'},
                {'url': 'https://www.reddit.com/r/VideoGeneration/', 'category': 'video_gen', 'type': 'reddit', 'name': 'Reddit Vidéo IA'},

                # 💻 PROGRAMMATION & CODING
                {'url': 'https://www.geeksforgeeks.org/', 'category': 'coding', 'type': 'geeksforgeeks', 'name': 'GeeksforGeeks'},
                {'url': 'https://www.theverge.com/ai-artificial-intelligence', 'category': 'general', 'type': 'theverge', 'name': 'The Verge'},

                # 🎵 MUSIQUE IA
                {'url': 'https://www.rollingstone.com/', 'category': 'fun', 'type': 'rollingstone', 'name': 'Rolling Stone'},

                # 🌟 ACTUALITÉS GÉNÉRALES IA ACCESSIBLES
                {'url': 'https://www.artificialintelligence-news.com/', 'category': 'general', 'type': 'ai_news', 'name': 'IA News'},
                {'url': 'https://venturebeat.com/category/ai/', 'category': 'general', 'type': 'venturebeat', 'name': 'VentureBeat'},
            ],

            'rss_feeds': [
                # 📡 FLUX RSS GRAND PUBLIC
                {'url': 'https://feeds.theverge.com/feed.xml', 'category': 'general', 'type': 'theverge', 'name': 'The Verge'},
                {'url': 'https://feeds.arstechnica.com/arstechnica/index', 'category': 'tech', 'type': 'arstechnica', 'name': 'Ars Technica'},

                # 🤖 MACHINE LEARNING & DATA ACCESSIBLE
                {'url': 'https://feeds.feedburner.com/kdnuggets-data-mining-analytics', 'category': 'ml', 'type': 'kdnuggets', 'name': 'KDnuggets'},
                {'url': 'https://www.deeplearning.ai/feed/', 'category': 'ml', 'type': 'deeplearning', 'name': 'Deep Learning.AI'},

                # 🎬 NVIDIA (GPU & IA hardware grand public)
                {'url': 'https://blogs.nvidia.com/feed/', 'category': 'general', 'type': 'nvidia', 'name': 'NVIDIA'},

                # 🎮 INDIE HACKERS & STARTUPS
                {'url': 'https://www.indiehackers.com/feed.xml', 'category': 'fun', 'type': 'indiehackers', 'name': 'Indie Hackers'},

                # 📰 POPULAR SCIENCE
                {'url': 'https://www.popsci.com/feed/', 'category': 'general', 'type': 'popsci', 'name': 'Popular Science'},

                # 🎵 MUSIQUE & CRÉATIF
                {'url': 'https://www.rollingstone.com/feed/', 'category': 'fun', 'type': 'rollingstone', 'name': 'Rolling Stone'},
            ],

            'special_sources': [
                # 🎯 SOURCES SPÉCIALES SYMPAS & ACCESSIBLES
                {'name': 'Product Hunt IA', 'url': 'https://www.producthunt.com/topics/artificial-intelligence', 'category': 'fun'},
                {'name': 'Zapier - Générateurs IA', 'url': 'https://zapier.com/blog/', 'category': 'image_gen'},
                {'name': 'PCMag - Tests IA', 'url': 'https://www.pcmag.com/news', 'category': 'image_gen'},
            ]
        }

        # Charger les actualités existantes
        self.news = self.load_news()

    def load_news(self):
        """Charger les actualités existantes depuis le fichier JSON"""
        if os.path.exists(self.news_file):
            try:
                with open(self.news_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erreur lors du chargement des actualités: {e}")
        return []

    def save_news(self):
        """Sauvegarder les actualités dans le fichier JSON"""
        try:
            # Garder seulement les 800 derniers articles (plus pour avoir du contenu)
            self.news = self.news[-800:]
            with open(self.news_file, 'w', encoding='utf-8') as f:
                json.dump(self.news, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ News sauvegardées: {len(self.news)} articles")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")

    def add_news_item(self, item):
        """Ajouter un nouvel article s'il n'existe pas déjà"""
        if not item.get('url'):
            return False

        # Vérifier si l'article existe déjà
        if any(existing['url'] == item['url'] for existing in self.news):
            return False

        # Enrichir l'item
        item['collected_at'] = datetime.now().isoformat()
        if 'published_date' not in item or not item['published_date']:
            item['published_date'] = datetime.now().strftime("%Y-%m-%d")

        self.news.append(item)
        logger.info(f"✅ {item.get('title', 'N/A')[:60]}")
        return True

    def scrape_website(self, site):
        """Scraper un site web pour récupérer les actualités"""
        logger.info(f"🌐 Scraping {site['url'][:50]}...")
        try:
            response = requests.get(site['url'], headers=self.headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Chercher tous les liens possibles
                articles = soup.find_all(['article', 'div', 'a'], class_=re.compile(r'post|article|entry|item|story|card|link', re.I))

                for article in articles[:20]:  # Augmenté à 20 articles par site
                    try:
                        # Chercher le titre
                        title_tag = article.find(['h1', 'h2', 'h3', 'h4', 'a', 'span'])
                        if not title_tag or not title_tag.get_text(strip=True):
                            continue

                        title = title_tag.get_text(strip=True)
                        if len(title) < 10:  # Filtrer les titres trop courts
                            continue

                        # Chercher l'URL
                        url_tag = article.find('a', href=True)
                        if not url_tag:
                            url_tag = article if article.name == 'a' else None
                        if not url_tag:
                            continue

                        url = url_tag['href']
                        if not url.startswith('http'):
                            url = urljoin(site['url'], url)

                        # Chercher la description
                        desc_tag = article.find(['p', 'div', 'span'], class_=re.compile(r'excerpt|summary|description|subtitle', re.I))
                        description = desc_tag.get_text(strip=True)[:300] if desc_tag else title

                        # Chercher une image
                        img_tag = article.find('img')
                        image_url = ''
                        if img_tag:
                            image_url = img_tag.get('src', img_tag.get('data-src', ''))
                            if image_url and not image_url.startswith('http'):
                                image_url = urljoin(site['url'], image_url)

                        news_item = {
                            'title': title[:200],
                            'url': url,
                            'description': description,
                            'image_url': image_url,
                            'published_date': datetime.now().strftime("%Y-%m-%d"),
                            'source': site['url'],
                            'source_type': 'website',
                            'category': site.get('category', 'general')
                        }

                        self.add_news_item(news_item)
                        time.sleep(random.uniform(0.3, 0.8))

                    except Exception as e:
                        logger.debug(f"Erreur parsing: {e}")
                        continue

        except Exception as e:
            logger.error(f"❌ Erreur {site['url'][:30]}: {str(e)[:50]}")

    def scrape_rss_feed(self, feed):
        """Scraper un flux RSS pour récupérer les actualités"""
        logger.info(f"📡 RSS {feed['url'][:40]}...")
        try:
            news_feed = feedparser.parse(feed['url'])

            for entry in news_feed.entries[:25]:  # Augmenté à 25
                try:
                    title = entry.get('title', '')
                    url = entry.get('link', '')
                    description = entry.get('summary', '')

                    if not title or not url:
                        continue

                    # Nettoyage de la description HTML
                    if description:
                        soup = BeautifulSoup(description, 'html.parser')
                        description = soup.get_text(strip=True)[:300]

                    # Récupérer la date
                    published_date = ''
                    if 'published' in entry:
                        published_date = entry['published'][:10]
                    elif 'updated' in entry:
                        published_date = entry['updated'][:10]

                    if not published_date:
                        published_date = datetime.now().strftime("%Y-%m-%d")

                    # Chercher une image
                    image_url = ''
                    if 'media_content' in entry:
                        for media in entry.media_content:
                            if 'url' in media:
                                image_url = media['url']
                                break

                    news_item = {
                        'title': title[:200],
                        'url': url,
                        'description': description,
                        'image_url': image_url,
                        'published_date': published_date,
                        'source': feed.get('type', 'rss'),
                        'source_type': 'rss',
                        'category': feed.get('category', 'general')
                    }

                    self.add_news_item(news_item)

                except Exception as e:
                    logger.debug(f"Erreur RSS: {e}")
                    continue

        except Exception as e:
            logger.error(f"❌ Erreur RSS {feed['url'][:30]}: {str(e)[:50]}")

    def scrape_special_sources(self):
        """Scraper les sources spéciales sympas"""
        logger.info("🎯 Sources spéciales...")

        # Product Hunt curated AI tools
        try:
            response = requests.get('https://www.producthunt.com/api/feed', headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('data', [])[:10]:
                    news_item = {
                        'title': item.get('name', '')[:200],
                        'url': f"https://www.producthunt.com/posts/{item.get('slug', '')}",
                        'description': item.get('tagline', '')[:300],
                        'image_url': item.get('thumbnail', {}).get('image_url', ''),
                        'published_date': datetime.now().strftime("%Y-%m-%d"),
                        'source': 'Product Hunt',
                        'source_type': 'producthunt',
                        'category': 'fun'
                    }
                    self.add_news_item(news_item)
        except:
            pass

    def scrape_influencers(self):
        """Récupérer les contenus des influenceurs AI"""
        logger.info("👤 Influenceurs IA...")

        curated_news = [
            {
                'title': '🚀 Top AI Influencers Updates',
                'description': 'Follow: Sam Altman, Andrej Karpathy, Yann LeCun, Jeremy Howard & Demis Hassabis',
                'category': 'trending',
                'source': 'AI Influencers'
            },
        ]

        for item in curated_news:
            news_item = {
                'title': item['title'],
                'url': 'https://twitter.com/search?q=%23AI%20-filter%3Areplies&type=latest',
                'description': item['description'],
                'image_url': '',
                'published_date': datetime.now().strftime("%Y-%m-%d"),
                'source': item['source'],
                'source_type': 'influencer',
                'category': item.get('category', 'general')
            }
            self.add_news_item(news_item)

    def run(self):
        """Exécuter le scraper complet"""
        logger.info("\n" + "="*70)
        logger.info("🚀 DÉMARRAGE SCRAPER IA NEWS - SOURCES FRAÎCHES!")
        logger.info("="*70)

        start_time = time.time()
        initial_count = len(self.news)

        # Scraper les sites web
        logger.info("\n📍 PHASE 1: Sites Web")
        for site in self.sources['sites']:
            self.scrape_website(site)
            time.sleep(random.uniform(1, 2))

        # Scraper les flux RSS
        logger.info("\n📡 PHASE 2: Flux RSS")
        for feed in self.sources['rss_feeds']:
            self.scrape_rss_feed(feed)
            time.sleep(random.uniform(0.5, 1.5))

        # Sources spéciales
        logger.info("\n🎯 PHASE 3: Sources Spéciales")
        self.scrape_special_sources()

        # Scraper les influenceurs
        logger.info("\n👤 PHASE 4: Influenceurs")
        self.scrape_influencers()

        # Sauvegarder les actualités
        self.save_news()

        elapsed_time = time.time() - start_time
        new_articles = len(self.news) - initial_count

        logger.info("\n" + "="*70)
        logger.info(f"✅ SCRAPING TERMINÉ!")
        logger.info(f"📊 Total: {len(self.news)} articles")
        logger.info(f"🆕 Nouveaux: {new_articles} articles")
        logger.info(f"⏱️  Durée: {elapsed_time:.2f}s")
        logger.info("="*70 + "\n")

        return len(self.news)

# Fonction principale pour exécuter le scraper
if __name__ == "__main__":
    scraper = IANewsScraper()
    scraper.run()
