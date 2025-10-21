# 🧠 IA News - Actualités en Intelligence Artificielle

> **Scraper automatique + Site web moderne pour les dernières actualités en IA**

Découvrez les dernières innovations en LLMs, Image Generation, Video Synthesis, Coding AI et bien plus encore. Actualités mises à jour automatiquement 24h/24, 7j/7.

## ✨ Caractéristiques

- 🤖 **Scraper automatique** - Collecte les données depuis 8+ sources spécialisées
- 🌐 **Site web moderne** - Design sleek, responsive, animations fluides
- 📱 **Mobile-first** - Parfait sur tous les appareils
- 🌓 **Dark mode** - Thème clair/sombre
- 🔄 **Auto-update** - Mise à jour toutes les 3 heures
- 📡 **Flux RSS** - S'abonner à un lecteur RSS standard
- 🔍 **Catégories** - Filtrez par LLMs, Image Gen, Video Gen, Coding, Fun AI
- 📊 **API** - Accédez aux données en JSON
- 🚀 **Déployable** - Docker, Netlify, AWS ready

## 🎯 Sources

Le scraper collecte depuis:

| Source | Type | Fréquence |
|--------|------|-----------|
| Hacker News | Web | 3h |
| The Verge | Web + RSS | 3h |
| Artificial Intelligence News | Web + RSS | 3h |
| VentureBeat | Web | 3h |
| Reddit (r/StableDiffusion) | Web | 3h |
| Reddit (r/OpenAI) | Web | 3h |
| KDnuggets | RSS | 3h |
| DeepLearning.AI | RSS | 3h |
| Ars Technica | RSS | 3h |

## 🚀 Installation Rapide

### Prérequis
- Python 3.8+
- pip ou conda

### 1. Cloner / Télécharger le projet

```bash
cd /chemin/vers/ia_news_site
```

### 2. Créer un environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Lancer le projet

```bash
# Option 1: Tout d'un coup (scraper + serveur)
python3 run.py all

# Option 2: Seulement le scraper
python3 run.py scraper

# Option 3: Seulement le serveur web
python3 run.py web
```

### 5. Accéder au site

Ouvrez votre navigateur et allez sur: **http://localhost:8001**

## 📖 Utilisation

### Ligne de commande

```bash
# Scraper seulement (update les données)
python3 -m scraper.scraper

# Démarrer le serveur web
cd website && python3 app.py

# Générer le site statique (pour Netlify)
python3 build_static.py

# Tout automatiser
python3 run.py all
```

### API Endpoints

```bash
# Récupérer les actualités (JSON)
GET http://localhost:8001/api/news?category=llms&limit=10

# Statistiques
GET http://localhost:8001/api/stats

# Flux RSS
GET http://localhost:8001/rss

# Rafraîchir manuellement
GET http://localhost:8001/refresh
```

### Cron (Auto-update)

Pour mettre à jour automatiquement toutes les 3 heures:

**Sur macOS/Linux:**
```bash
crontab -e
# Ajouter:
0 */3 * * * cd /chemin/vers/ia_news_site && python3 run_update_and_build.py
```

**Sur Windows:**
```bash
schtasks /create /tn "IA News" /tr "python C:\path\to\run_update_and_build.py" /sc HOURLY /mo 3
```

## 🎨 Design

Le site utilise:
- **Couleurs modernes**: Indigo, Pink, Cyan (Tailwind palette)
- **Typographie**: Inter sans-serif
- **Animations**: Transitions fluides, micro-interactions
- **Responsive**: Grid CSS, flexbox, mobile-first
- **Dark mode**: Support complet avec localStorage

### Structure du Projet

```
ia_news_site/
├── scraper/
│   └── scraper.py           # Cœur du scraper
├── website/
│   ├── app.py               # Flask app
│   ├── static/
│   │   └── css/style.css     # Styles modernes
│   └── templates/
│       ├── base.html         # Layout de base
│       └── index.html        # Page d'accueil
├── data/
│   └── ia_news.json         # Base de données (JSON)
├── logs/
│   └── update.log           # Logs du scraper
├── requirements.txt         # Dépendances Python
├── run.py                   # Point d'entrée principal
├── README.md                # Ce fichier
└── DEPLOYMENT.md            # Guide de déploiement
```

## 🚀 Déploiement

### Sur Netlify

1. Générer le site statique: `python3 build_static.py`
2. Commiter les changements: `git add . && git commit -m "Update"`
3. Connecter GitHub à Netlify
4. Build command: `python3 build_static.py`
5. Publish: `_site/`

### Avec Docker

```bash
docker build -t ia-news .
docker run -p 8001:8001 ia-news
```

### Sur un serveur (Linux)

Voir [DEPLOYMENT.md](DEPLOYMENT.md) pour les instructions complètes.

## 🔧 Configuration

Créer un `.env` pour les variables:

```env
FLASK_ENV=production
FLASK_DEBUG=False
SCRAPER_INTERVAL=3
LOG_LEVEL=INFO
```

## 📊 Performance

- ⚡ Scraper: ~30-60 secondes pour toutes les sources
- 📄 Pages: < 1MB HTML statique
- 🔒 Caching: 500 articles max pour perfs optimales
- 🌐 Rate limiting: Délais entre sources respectés

## 🤝 Contribution

Les contributions sont bienvenues! Vous pouvez:
- ➕ Ajouter de nouvelles sources
- 🎨 Améliorer le design
- 🐛 Signaler des bugs
- 💡 Proposer des améliorations

## 📝 License

MIT - Libre d'utilisation

## ⚙️ Troubleshooting

**Q: Pas d'articles affichés?**
A: Lancer le scraper d'abord: `python3 run.py scraper`

**Q: Port 8001 occupé?**
A: Changer le port dans `website/app.py` ou tuer le processus

**Q: Données ne s'actualisent pas?**
A: Vérifier le cron: `crontab -l` et les logs: `tail -f logs/update.log`

## 📞 Support

Pour toute question ou problème:
1. Vérifier [DEPLOYMENT.md](DEPLOYMENT.md)
2. Vérifier les logs dans `logs/update.log`
3. Lancer en mode debug: `python3 -c "from scraper.scraper import IANewsScraper; IANewsScraper().run()"`

---

**Fait avec ❤️ en Python**

Dernière mise à jour: octobre 2024
