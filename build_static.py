#!/usr/bin/env python3
"""
Build static HTML from news JSON and templates
For use with GitHub Actions + Netlify
"""

import os
import json
import shutil
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime, timedelta
import sys

# --- Configuration ---
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(ROOT_DIR, 'website', 'templates')
STATIC_SOURCE_DIR = os.path.join(ROOT_DIR, 'website', 'static')
DATA_FILE = os.path.join(ROOT_DIR, 'data', 'ia_news.json')
OUTPUT_DIR = os.path.join(ROOT_DIR, 'public')  # Netlify publiera ce dossier

# --- Fonctions utilitaires Jinja ---
def format_date_filter(value, format_str='%d %B %Y'):
    """
    Filtre Jinja pour formater les dates.
    S'attend à une chaîne ISO 8601 ou un objet datetime.
    """
    if not value:
        return "Date non spécifiée"
    if isinstance(value, str):
        try:
            # Gérer les formats ISO avec ou sans 'Z', avec ou sans microsecondes
            value_cleaned = value.replace('Z', '+00:00')
            if '.' in value_cleaned and '+' in value_cleaned.split('.')[1]: # Format avec microsecondes et timezone
                 dt_object = datetime.fromisoformat(value_cleaned)
            elif '.' in value_cleaned: # Format avec microsecondes sans timezone explicite (on suppose UTC)
                 dt_object = datetime.strptime(value_cleaned.split('.')[0], '%Y-%m-%dT%H:%M:%S').replace(microsecond=int(value_cleaned.split('.')[1].rstrip('Z')[:6]))
            else: # Format sans microsecondes
                 dt_object = datetime.fromisoformat(value_cleaned)
        except ValueError:
            return value # Retourner la valeur originale si le parsing échoue
    elif isinstance(value, datetime):
        dt_object = value
    else:
        return value # Type inconnu

    return dt_object.strftime(format_str)

def generate_unique_slug(text, existing_slugs_set):
    """Génère un slug unique en ajoutant un compteur si nécessaire."""
    import re
    # Simple slug generation without slugify
    base_slug = re.sub(r'[^a-z0-9]+', '-', text.lower())[:80].strip('-')
    if not base_slug:
        base_slug = "article"
    slug = base_slug
    counter = 1
    while slug in existing_slugs_set:
        slug = f"{base_slug}-{counter}"
        counter += 1
    existing_slugs_set.add(slug)
    return slug

def custom_url_for(endpoint, **values):
    """
    Simule url_for pour un site statique.
    Les chemins sont relatifs à la racine du site.
    """
    if endpoint == 'static':
        return f"/static/{values['filename']}" # Netlify servira /static/*
    if endpoint == 'home':
        query_params = []
        if 'source' in values and values['source']:
            # Pour un site statique, les filtres via query params sur la page d'accueil
            # nécessitent du JS côté client ou des pages pré-générées par filtre.
            # Ici, on génère un lien qui pourrait être utilisé par du JS.
            query_params.append(f"source={values['source']}")

        base_url = "/" # La page d'accueil est à la racine
        if query_params:
            return f"{base_url}?{'&'.join(query_params)}"
        return base_url

    if endpoint == 'article_detail_page': # Nom utilisé pour lier vers un article
        slug = values.get('article_slug', 'default-slug')
        return f"/article/{slug}.html"

    if endpoint == 'archives':
        return "/archives/"

    if endpoint == 'archives_category':
        category = values.get('category', 'all')
        return f"/archives/{category}/"

    # Fallback pour d'autres endpoints non gérés
    return f"/{endpoint}/not-configured/"

def separate_articles_by_date(articles):
    """Sépare les articles en récents (< 7 jours) et archives (>= 7 jours)"""
    now = datetime.now()
    seven_days_ago = now - timedelta(days=7)

    recent_articles = []
    archived_articles = []

    for article in articles:
        try:
            date_str = article.get('published_date', '')
            if isinstance(date_str, str):
                # Parser la date
                date_obj = datetime.strptime(date_str.split('T')[0], '%Y-%m-%d')
                if date_obj >= seven_days_ago:
                    recent_articles.append(article)
                else:
                    archived_articles.append(article)
            else:
                recent_articles.append(article)
        except:
            recent_articles.append(article)

    return recent_articles, archived_articles

def organize_archives(articles):
    """Organise les articles archivés par catégorie et mois"""
    organized = {}

    for article in articles:
        category = article.get('category', 'general')
        date_str = article.get('published_date', '')

        # Extraire le mois et l'année
        try:
            date_obj = datetime.strptime(date_str.split('T')[0], '%Y-%m-%d')
            month_key = date_obj.strftime('%Y-%m')  # Format: 2024-10
            month_label = date_obj.strftime('%B %Y')  # Format: October 2024
        except:
            month_key = 'unknown'
            month_label = 'Unknown Date'

        # Créer la structure imbriquée
        if category not in organized:
            organized[category] = {}
        if month_key not in organized[category]:
            organized[category][month_key] = {
                'label': month_label,
                'articles': []
            }

        organized[category][month_key]['articles'].append(article)

    # Trier par date décroissante
    for category in organized:
        for month in organized[category]:
            organized[category][month]['articles'].sort(
                key=lambda x: x.get('published_date', ''),
                reverse=True
            )

    return organized

# --- Script principal de génération ---
def build_site():
    print("Début de la génération du site statique...")

    # 0. Nettoyer/Créer le dossier de sortie
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    articles_output_dir = os.path.join(OUTPUT_DIR, 'article')
    os.makedirs(articles_output_dir)
    archives_output_dir = os.path.join(OUTPUT_DIR, 'archives')
    os.makedirs(archives_output_dir)

    # 1. Charger les données
    print(f"Chargement des données depuis {DATA_FILE}...")
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        all_news_items = json.load(f)

    # 1.5 Séparer récents et archives
    recent_articles, archived_articles = separate_articles_by_date(all_news_items)
    organized_archives = organize_archives(archived_articles)
    print(f"📊 Articles récents: {len(recent_articles)} | Archives: {len(archived_articles)}")

    # 2. Préparer l'environnement Jinja2
    jinja_env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True,
        lstrip_blocks=True
    )
    jinja_env.filters['format_date'] = format_date_filter
    jinja_env.filters['capitalize'] = lambda s: str(s).capitalize() if s else ''
    jinja_env.globals['url_for'] = custom_url_for # Rendre url_for disponible dans tous les templates

    # 3. Pré-traiter les articles (ajouter slugs uniques, etc.)
    print("Pré-traitement des articles (ajout de slugs)...")
    processed_recent = []
    processed_archived = []
    article_slugs = set()

    for index, item in enumerate(recent_articles):
        item['id'] = item.get('id', index)
        title_for_slug = item.get('title_fr') or item.get('title') or f"sans-titre-{item['id']}"
        item['slug'] = generate_unique_slug(title_for_slug, article_slugs)
        processed_recent.append(item)

    for index, item in enumerate(archived_articles):
        item['id'] = item.get('id', f"archive-{index}")
        title_for_slug = item.get('title_fr') or item.get('title') or f"sans-titre-{item['id']}"
        item['slug'] = generate_unique_slug(title_for_slug, article_slugs)
        processed_archived.append(item)

    all_processed = processed_recent + processed_archived

    # 4. Générer les pages d'articles
    print(f"Génération des pages d'articles dans {articles_output_dir}...")
    article_template = jinja_env.get_template('article.html')
    for article_data in all_processed:
        related_candidates = [art for art in all_processed if art['id'] != article_data['id']]
        related_articles_list = related_candidates[:min(3, len(related_candidates))]

        html_page_content = article_template.render(
            article=article_data,
            related_articles=related_articles_list,
            news=all_processed
        )
        with open(os.path.join(articles_output_dir, f"{article_data['slug']}.html"), 'w', encoding='utf-8') as f:
            f.write(html_page_content)
    print(f"{len(all_processed)} pages d'articles générées.")

    # 4.5 Générer les pages d'archives par catégorie
    print(f"Génération des pages d'archives...")
    archives_template = jinja_env.get_template('archives.html')

    for category, months in organized_archives.items():
        # Créer un sous-dossier par catégorie
        category_dir = os.path.join(archives_output_dir, category.lower().replace(' ', '-'))
        os.makedirs(category_dir, exist_ok=True)

        # Page d'accueil de la catégorie
        category_archives = [art for art in processed_archived if art.get('category') == category]
        archives_content = archives_template.render(
            category=category,
            months=months,
            archives=category_archives,
            organized_archives=organized_archives
        )
        with open(os.path.join(category_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(archives_content)

    # Page générale des archives
    archives_main = archives_template.render(
        category='all',
        months=organized_archives,
        archives=processed_archived,
        organized_archives=organized_archives
    )
    with open(os.path.join(archives_output_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(archives_main)

    print(f"Pages d'archives générées pour {len(organized_archives)} catégories")

    # 5. Générer la page d'accueil (SEULEMENT articles récents)
    print(f"Génération de la page d'accueil ({os.path.join(OUTPUT_DIR, 'index.html')})...")
    home_template = jinja_env.get_template('index.html')
    home_html_content = home_template.render(
        news=processed_recent,  # SEULEMENT les articles récents!
        recent_count=len(processed_recent),
        archive_count=len(processed_archived)
    )
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(home_html_content)

    # 6. Copier les fichiers statiques (CSS, JS, images)
    print(f"Copie des fichiers statiques de {STATIC_SOURCE_DIR} vers {os.path.join(OUTPUT_DIR, 'static')}...")
    if os.path.exists(STATIC_SOURCE_DIR):
        shutil.copytree(STATIC_SOURCE_DIR, os.path.join(OUTPUT_DIR, 'static'), dirs_exist_ok=True)
    else:
        print(f"AVERTISSEMENT: Le dossier statique source {STATIC_SOURCE_DIR} n'existe pas.")

    print("Génération du site statique terminée !")
    print(f"Le site a été généré dans : {OUTPUT_DIR}")
    print(f"📰 Page d'accueil: {len(processed_recent)} articles récents")
    print(f"📚 Archives: {len(processed_archived)} articles archivés")

if __name__ == '__main__':
    build_site()
