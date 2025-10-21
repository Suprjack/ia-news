import requests
import json
import re
import os
from datetime import datetime, timedelta
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

# Configuration du filtre de date
MAX_ARTICLE_AGE_HOURS = 24  # Ne garder que les articles des dernières 24 heures

class IANewsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        self.news_file = os.path.join(self.data_dir, 'ia_news.json')

        # 🎯 SOURCES LLM & IA ACCESSIBLES - FOCUS SUR L'ACTUALITÉ RÉCENTE
        self.sources = {
            'rss_feeds': [
                # 🤖 SOURCES PRINCIPALES LLM & IA
                {'url': 'https://openai.com/blog/rss.xml', 'category': 'llms', 'type': 'openai', 'name': 'OpenAI Blog'},
                {'url': 'https://www.anthropic.com/news/rss.xml', 'category': 'llms', 'type': 'anthropic', 'name': 'Anthropic News'},
                {'url': 'https://blog.google/technology/ai/rss/', 'category': 'llms', 'type': 'google', 'name': 'Google AI Blog'},
                {'url': 'https://huggingface.co/blog/feed.xml', 'category': 'llms', 'type': 'huggingface', 'name': 'Hugging Face Blog'},
                
                # 📰 TECH NEWS - IA FOCUS
                {'url': 'https://www.theverge.com/rss/ai-artificial-intelligence/index.xml', 'category': 'general', 'type': 'theverge', 'name': 'The Verge AI'},
                {'url': 'https://techcrunch.com/category/artificial-intelligence/feed/', 'category': 'general', 'type': 'techcrunch', 'name': 'TechCrunch AI'},
                {'url': 'https://venturebeat.com/category/ai/feed/', 'category': 'general', 'type': 'venturebeat', 'name': 'VentureBeat AI'},
                {'url': 'https://www.technologyreview.com/topic/artificial-intelligence/feed', 'category': 'general', 'type': 'mittr', 'name': 'MIT Technology Review AI'},
                
                # 🔬 TECH & SCIENCE
                {'url': 'https://feeds.arstechnica.com/arstechnica/technology-lab', 'category': 'tech', 'type': 'arstechnica', 'name': 'Ars Technica'},
                {'url': 'https://www.wired.com/feed/tag/ai/latest/rss', 'category': 'general', 'type': 'wired', 'name': 'Wired AI'},
                {'url': 'https://www.artificialintelligence-news.com/feed/', 'category': 'general', 'type': 'ainews', 'name': 'AI News'},
                
                # 🎮 NVIDIA & HARDWARE
                {'url': 'https://blogs.nvidia.com/feed/', 'category': 'hardware', 'type': 'nvidia', 'name': 'NVIDIA Blog'},
                
                # 📊 ML & DATA SCIENCE
                {'url': 'https://feeds.feedburner.com/kdnuggets-data-mining-analytics', 'category': 'ml', 'type': 'kdnuggets', 'name': 'KDnuggets'},
                {'url': 'https://www.deeplearning.ai/feed/', 'category': 'ml', 'type': 'deeplearning', 'name': 'DeepLearning.AI'},
                
                # 🚀 STARTUPS & INNOVATION
                {'url': 'https://www.indiehackers.com/feed.xml', 'category': 'startups', 'type': 'indiehackers', 'name': 'Indie Hackers'},
            ],

            'sites': [
                # Sites web à scraper (backup si RSS ne fonctionne pas)
                {'url': 'https://openai.com/blog/', 'category': 'llms', 'type': 'openai', 'name': 'OpenAI Blog'},
                {'url': 'https://www.anthropic.com/news', 'category': 'llms', 'type': 'anthropic', 'name': 'Anthropic News'},
                {'url': 'https://blog.google/technology/ai/', 'category': 'llms', 'type': 'google', 'name': 'Google AI'},
                {'url': 'https://huggingface.co/blog', 'category': 'llms', 'type': 'huggingface', 'name': 'Hugging Face'},
                {'url': 'https://www.theverge.com/ai-artificial-intelligence', 'category': 'general', 'type': 'theverge', 'name': 'The Verge AI'},
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
            # Trier par date (plus récent en premier)
            self.news.sort(key=lambda x: x.get('published_date', ''), reverse=True)
            # Garder seulement les 500 derniers articles
            self.news = self.news[:500]
            with open(self.news_file, 'w', encoding='utf-8') as f:
                json.dump(self.news, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ News sauvegardées: {len(self.news)} articles")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {e}")

    def is_recent_article(self, published_date, max_hours=MAX_ARTICLE_AGE_HOURS):
        """Vérifier si un article a été publié dans les dernières max_hours heures"""
        if not published_date:
            logger.debug("❌ Article rejeté: pas de date disponible")
            return False
        
        try:
            # Parser la date de publication
            if isinstance(published_date, str):
                # Essayer différents formats
                formats = [
                    "%Y-%m-%d",
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S.%f",
                    "%Y-%m-%dT%H:%M:%S%z",
                    "%Y-%m-%d %H:%M:%S",
                ]
                
                article_date = None
                for fmt in formats:
                    try:
                        # Nettoyer la date pour enlever les timezone si présentes
                        clean_date = published_date.split('+')[0].split('Z')[0].strip()
                        article_date = datetime.strptime(clean_date, fmt)
                        break
                    except:
                        continue
                
                if not article_date:
                    logger.debug(f"❌ Article rejeté: format de date non reconnu ({published_date})")
                    return False
            else:
                article_date = published_date
            
            # Calculer la différence avec maintenant
            now = datetime.now()
            time_diff = now - article_date
            
            # Vérifier si l'article est dans la fenêtre de temps
            if time_diff.total_seconds() < 0:
                # Article dans le futur (peut arriver avec des timezone)
                logger.debug(f"⚠️  Article dans le futur ignoré: {published_date}")
                return False
            
            hours_old = time_diff.total_seconds() / 3600
            
            if hours_old <= max_hours:
                return True
            else:
                logger.debug(f"❌ Article trop vieux: {hours_old:.1f}h ({published_date})")
                return False
                
        except Exception as e:
            logger.debug(f"❌ Erreur validation date: {e}")
            return False

    def add_news_item(self, item):
        """Ajouter un nouvel article s'il n'existe pas déjà et s'il est récent"""
        if not item.get('url'):
            return False

        # Vérifier si l'article existe déjà
        if any(existing['url'] == item['url'] for existing in self.news):
            return False

        # Enrichir l'item
        item['collected_at'] = datetime.now().isoformat()
        if 'published_date' not in item or not item['published_date']:
            item['published_date'] = datetime.now().strftime("%Y-%m-%d")
        
        # Vérifier si l'article est récent (filtre 24h)
        if not self.is_recent_article(item['published_date']):
            logger.debug(f"⏰ Article ignoré (trop vieux): {item.get('title', 'N/A')[:60]}")
            return False

        self.news.append(item)
        logger.info(f"✅ {item.get('source', 'N/A')}: {item.get('title', 'N/A')[:60]}")
        return True

    def parse_date(self, date_string):
        """Parser une date depuis différents formats"""
        if not date_string:
            return datetime.now().strftime("%Y-%m-%d")
        
        try:
            # Essayer différents formats
            formats = [
                "%a, %d %b %Y %H:%M:%S %z",
                "%a, %d %b %Y %H:%M:%S %Z",
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_string[:25], fmt)
                    return dt.strftime("%Y-%m-%d")
                except:
                    continue
            
            # Si aucun format ne fonctionne, retourner la date actuelle
            return datetime.now().strftime("%Y-%m-%d")
        except:
            return datetime.now().strftime("%Y-%m-%d")

    def scrape_rss_feed(self, feed):
        """Scraper un flux RSS pour récupérer les actualités"""
        logger.info(f"📡 RSS: {feed['name']}")
        try:
            news_feed = feedparser.parse(feed['url'])

            if not news_feed.entries:
                logger.warning(f"⚠️  Aucune entrée trouvée pour {feed['name']}")
                return

            for entry in news_feed.entries[:30]:  # Limiter à 30 articles par feed
                try:
                    title = entry.get('title', '').strip()
                    url = entry.get('link', '').strip()
                    
                    if not title or not url:
                        continue

                    # Nettoyage de la description HTML
                    description = ''
                    if 'summary' in entry:
                        soup = BeautifulSoup(entry['summary'], 'html.parser')
                        description = soup.get_text(strip=True)[:400]
                    elif 'description' in entry:
                        soup = BeautifulSoup(entry['description'], 'html.parser')
                        description = soup.get_text(strip=True)[:400]
                    
                    if not description:
                        description = title

                    # Récupérer la date
                    published_date = ''
                    if 'published' in entry:
                        published_date = self.parse_date(entry['published'])
                    elif 'updated' in entry:
                        published_date = self.parse_date(entry['updated'])
                    else:
                        published_date = datetime.now().strftime("%Y-%m-%d")

                    # Chercher une image
                    image_url = ''
                    
                    # Méthode 1: media_content
                    if hasattr(entry, 'media_content') and entry.media_content:
                        for media in entry.media_content:
                            if 'url' in media:
                                image_url = media['url']
                                break
                    
                    # Méthode 2: media_thumbnail
                    if not image_url and hasattr(entry, 'media_thumbnail') and entry.media_thumbnail:
                        image_url = entry.media_thumbnail[0].get('url', '')
                    
                    # Méthode 3: chercher dans le contenu
                    if not image_url and 'content' in entry:
                        for content in entry.content:
                            soup = BeautifulSoup(content.value, 'html.parser')
                            img = soup.find('img')
                            if img and img.get('src'):
                                image_url = img['src']
                                break
                    
                    # Méthode 4: chercher dans summary
                    if not image_url and 'summary' in entry:
                        soup = BeautifulSoup(entry['summary'], 'html.parser')
                        img = soup.find('img')
                        if img and img.get('src'):
                            image_url = img['src']

                    news_item = {
                        'title': title[:200],
                        'url': url,
                        'description': description,
                        'image_url': image_url,
                        'published_date': published_date,
                        'source': feed.get('name', 'RSS'),
                        'source_type': 'rss',
                        'category': feed.get('category', 'general')
                    }

                    self.add_news_item(news_item)

                except Exception as e:
                    logger.debug(f"Erreur parsing entrée RSS: {e}")
                    continue

        except Exception as e:
            logger.error(f"❌ Erreur RSS {feed['name']}: {str(e)[:100]}")

    def scrape_website(self, site):
        """Scraper un site web pour récupérer les actualités"""
        logger.info(f"🌐 Web: {site['name']}")
        try:
            response = requests.get(site['url'], headers=self.headers, timeout=15)
            if response.status_code != 200:
                logger.warning(f"⚠️  Status {response.status_code} pour {site['name']}")
                return

            soup = BeautifulSoup(response.text, 'html.parser')

            # Stratégies de scraping selon le type de site
            articles = []
            
            # Chercher les articles avec différentes stratégies
            selectors = [
                'article',
                '[class*="post"]',
                '[class*="article"]',
                '[class*="entry"]',
                '[class*="story"]',
                '[class*="card"]',
            ]
            
            for selector in selectors:
                found = soup.select(selector)
                if found:
                    articles.extend(found[:20])
                    break

            if not articles:
                logger.warning(f"⚠️  Aucun article trouvé pour {site['name']}")
                return

            for article in articles[:15]:  # Limiter à 15 articles par site
                try:
                    # Chercher le titre
                    title_tag = article.find(['h1', 'h2', 'h3', 'h4'])
                    if not title_tag:
                        title_tag = article.find('a')
                    
                    if not title_tag:
                        continue

                    title = title_tag.get_text(strip=True)
                    if len(title) < 10:
                        continue

                    # Chercher l'URL
                    url_tag = article.find('a', href=True)
                    if not url_tag:
                        continue

                    url = url_tag['href']
                    if not url.startswith('http'):
                        url = urljoin(site['url'], url)

                    # Chercher la description
                    desc_tag = article.find(['p', 'div'], class_=re.compile(r'excerpt|summary|description|subtitle|deck', re.I))
                    description = desc_tag.get_text(strip=True)[:400] if desc_tag else title

                    # Chercher une image
                    img_tag = article.find('img')
                    image_url = ''
                    if img_tag:
                        image_url = img_tag.get('src', img_tag.get('data-src', ''))
                        if image_url and not image_url.startswith('http'):
                            image_url = urljoin(site['url'], image_url)

                    # Chercher la date
                    date_tag = article.find(['time', 'span'], class_=re.compile(r'date|time|published', re.I))
                    published_date = datetime.now().strftime("%Y-%m-%d")
                    if date_tag:
                        date_str = date_tag.get('datetime', date_tag.get_text(strip=True))
                        published_date = self.parse_date(date_str)

                    news_item = {
                        'title': title[:200],
                        'url': url,
                        'description': description,
                        'image_url': image_url,
                        'published_date': published_date,
                        'source': site.get('name', 'Web'),
                        'source_type': 'website',
                        'category': site.get('category', 'general')
                    }

                    self.add_news_item(news_item)

                except Exception as e:
                    logger.debug(f"Erreur parsing article: {e}")
                    continue

            time.sleep(random.uniform(1, 2))

        except Exception as e:
            logger.error(f"❌ Erreur {site['name']}: {str(e)[:100]}")

    def run(self):
        """Exécuter le scraper complet"""
        logger.info("\n" + "="*70)
        logger.info("🚀 SCRAPER IA NEWS - FOCUS LLM & ACTUALITÉS RÉCENTES")
        logger.info(f"⏰ Filtre: Articles des dernières {MAX_ARTICLE_AGE_HOURS}h uniquement")
        logger.info("="*70)

        start_time = time.time()
        initial_count = len(self.news)
        rejected_count = 0

        # PHASE 1: Scraper les flux RSS (prioritaire pour avoir des dates précises)
        logger.info("\n📡 PHASE 1: Flux RSS (sources principales)")
        for feed in self.sources['rss_feeds']:
            self.scrape_rss_feed(feed)
            time.sleep(random.uniform(0.5, 1.5))

        # PHASE 2: Scraper les sites web (backup)
        logger.info("\n🌐 PHASE 2: Sites Web (backup)")
        for site in self.sources['sites']:
            self.scrape_website(site)
            time.sleep(random.uniform(1, 2))

        # Sauvegarder les actualités
        self.save_news()

        elapsed_time = time.time() - start_time
        new_articles = len(self.news) - initial_count

        logger.info("\n" + "="*70)
        logger.info(f"✅ SCRAPING TERMINÉ!")
        logger.info(f"📊 Total: {len(self.news)} articles")
        logger.info(f"🆕 Nouveaux: {new_articles} articles")
        logger.info(f"⏰ Filtre: Dernières {MAX_ARTICLE_AGE_HOURS}h")
        logger.info(f"⏱️  Durée: {elapsed_time:.2f}s")
        logger.info("="*70 + "\n")

        return len(self.news)

# Fonction principale pour exécuter le scraper
if __name__ == "__main__":
    scraper = IANewsScraper()
    scraper.run()
