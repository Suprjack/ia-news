#!/usr/bin/env python3
"""
IA News - Main Entry Point
Scrape AI news and serve on Flask web server
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Add project to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from scraper.scraper import IANewsScraper

def run_scraper():
    """Run the scraper"""
    print("\n" + "="*70)
    print("🤖 Lancement du Scraper IA News")
    print("="*70 + "\n")
    try:
        scraper = IANewsScraper()
        count = scraper.run()
        print(f"\n✅ Scraper terminé avec succès!")
        print(f"📊 Total d'articles: {count}")
        return True
    except Exception as e:
        print(f"\n❌ Erreur lors du scraping: {e}")
        return False

def run_web_server():
    """Run the Flask web server"""
    print("\n" + "="*70)
    print("🌐 Lancement du serveur web")
    print("="*70 + "\n")
    try:
        web_dir = PROJECT_ROOT / 'website'
        os.chdir(web_dir)

        # Try to import flask
        try:
            from app import app
            print(f"📍 Serveur accessible sur: http://localhost:8001")
            print(f"📊 API: http://localhost:8001/api/news")
            print(f"🔄 RSS: http://localhost:8001/rss")
            print(f"🔄 Rafraîchir: http://localhost:8001/refresh")
            print("\n⌨️  Appuyez sur Ctrl+C pour arrêter\n")
            app.run(host='0.0.0.0', port=8001, debug=True)
        except ImportError:
            print("❌ Flask n'est pas installé. Exécutez: pip install -r requirements.txt")
            return False

    except Exception as e:
        print(f"❌ Erreur lors du lancement du serveur: {e}")
        return False

def run_both():
    """Run scraper and web server"""
    # First run scraper
    if run_scraper():
        # Then run web server
        run_web_server()

def main():
    parser = argparse.ArgumentParser(
        description='IA News - Scraper et serveur web d\'actualités IA',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python3 run.py scraper          # Lance le scraper seulement
  python3 run.py web              # Lance le serveur web seulement
  python3 run.py all              # Lance les deux (scraper puis serveur)
  python3 run.py --help           # Affiche cette aide
        """
    )

    parser.add_argument(
        'command',
        nargs='?',
        default='all',
        choices=['scraper', 'web', 'all'],
        help='Commande à exécuter (défaut: all)'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Mode debug activé'
    )

    args = parser.parse_args()

    print("""
╔═══════════════════════════════════════════════════════════════════════╗
║                   IA News - Actualités IA                            ║
║              Scrapin automatique + Serveur Web Flask                 ║
╚═══════════════════════════════════════════════════════════════════════╝
    """)

    if args.command == 'scraper' or args.command == 'all':
        success = run_scraper()
        if args.command == 'scraper':
            sys.exit(0 if success else 1)

    if args.command == 'web' or args.command == 'all':
        run_web_server()

    if args.command == 'all' and not success:
        print("\n⚠️  Le scraper a échoué, mais le serveur web démarre quand même.")
        run_web_server()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Au revoir!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)
