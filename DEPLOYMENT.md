# 🚀 Guide de Déploiement - IA News

## Installation Rapide

### 1. **Prérequis**
```bash
Python 3.8+
pip
virtualenv (optionnel mais recommandé)
```

### 2. **Installation des Dépendances**

```bash
# Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### 3. **Lancer le Scraper Initial**

```bash
# Scraper pour la première fois
python3 -m scraper.scraper

# Ou avec le wrapper
python3 run_update_and_build.py
```

### 4. **Lancer le Site Web**

```bash
# Démarrer le serveur Flask
cd website
python3 app.py

# Le site sera accessible sur:
# http://localhost:8001
```

## Configuration Automatisée (Cron)

Pour mettre à jour les actualités automatiquement toutes les 3 heures:

### Sur macOS/Linux:

```bash
# Ouvrir l'éditeur crontab
crontab -e

# Ajouter cette ligne:
0 */3 * * * cd /chemin/vers/ia_news_site && /path/to/venv/bin/python3 run_update_and_build.py >> /var/log/ia_news.log 2>&1
```

### Sur Windows:

Utiliser Task Scheduler ou l'outil `schtasks`:

```bash
schtasks /create /tn "IA News Scraper" /tr "python C:\path\to\run_update_and_build.py" /sc HOURLY /mo 3
```

## Déploiement sur Netlify

### 1. **Générer le site statique**

```bash
python3 build_static.py
```

Cela créera un dossier `_site/` avec les fichiers HTML statiques.

### 2. **Connecter à GitHub**

```bash
git add .
git commit -m "Update news site"
git push origin master
```

### 3. **Configurer Netlify**

1. Aller sur [netlify.com](https://netlify.com)
2. Connecter votre repo GitHub
3. Build command: `python3 build_static.py`
4. Publish directory: `_site`

## Déploiement avec Docker

### Dockerfile inclus

```bash
# Builder l'image
docker build -t ia-news .

# Lancer le container
docker run -p 8001:8001 ia-news

# Ou avec docker-compose
docker-compose up
```

## Configuration Environnement

Créer un fichier `.env` à la racine:

```
# .env
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=sqlite:///ia_news.db
LOG_LEVEL=INFO
SCRAPER_INTERVAL=3  # heures
```

## Endpoints API

### Récupérer les actualités
```bash
GET /api/news?category=llms&limit=10
```

### Statistiques
```bash
GET /api/stats
```

### Flux RSS
```bash
GET /rss
```

## Troubleshooting

### Erreur: "Module scraper not found"
```bash
# Solution: installer depuis le bon répertoire
cd /chemin/vers/ia_news_site
python3 -m scraper.scraper
```

### Erreur: "Port 8001 already in use"
```bash
# Tuer le processus
lsof -i :8001
kill -9 <PID>

# Ou changer le port dans app.py
```

### Articles ne s'actualisent pas
- Vérifier que le cron est actif: `crontab -l`
- Vérifier les logs: `tail -f /var/log/ia_news.log`
- Tester manuellement: `python3 run_update_and_build.py`

## Performance & Optimisation

- **Cache**: Les articles sont mis en cache dans `data/ia_news.json`
- **Scraping**: Limité à 500 articles maximum pour éviter les ralentissements
- **Requêtes**: Rate limiting (délai entre chaque source)

## Sécurité

⚠️ **À faire avant production:**

1. Changer `app.secret_key` dans `website/app.py`
2. Configurer HTTPS/SSL
3. Ajouter authentification si nécessaire
4. Configurer CORS si API publique
5. Ajouter rate limiting

## Support & Aide

Pour des questions ou des problèmes:
1. Vérifier les logs dans `logs/update.log`
2. Lancer le scraper en mode debug: `python3 -c "from scraper.scraper import IANewsScraper; IANewsScraper().run()"`
3. Vérifier que les sources sont accessibles
