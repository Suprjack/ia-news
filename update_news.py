#!/usr/bin/env python3
"""
Script de mise à jour automatique des actualités IA
Ce script est destiné à être exécuté par cron pour mettre à jour régulièrement les actualités
"""

import os
import sys
import logging
from datetime import datetime
from scraper.scraper import IANewsScraper

# Configuration du logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'update.log')

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Fonction principale pour exécuter la mise à jour des actualités"""
    try:
        logging.info("Démarrage de la mise à jour des actualités IA...")
        start_time = datetime.now()
        
        # Exécuter le scraper
        scraper = IANewsScraper()
        num_news = scraper.run()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logging.info(f"Mise à jour terminée. {num_news} articles trouvés en {duration:.2f} secondes.")
        
        # Commit and push changes to Git
        try:
            logging.info("Commiting changes to git...")
            subprocess.run(["git", "add", "data/ia_news.json", "public"], check=True, cwd=os.getcwd())
            subprocess.run(["git", "commit", "-m", "Update news and regenerate site"], check=True, cwd=os.getcwd())
            logging.info("Pushing changes to git...")
            subprocess.run(["git", "push"], check=True, cwd=os.getcwd())
            logging.info("Changes pushed to git successfully.")
        except Exception as git_err:
            logging.error(f"Erreur lors du commit/push Git : {str(git_err)}")
        
        return 0
    except Exception as e:
        logging.error(f"Erreur lors de la mise à jour : {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
