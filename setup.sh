#!/bin/bash

# Script d'installation et de démarrage pour ActualitésIA
echo "Installation d'ActualitésIA..."

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "Python 3 n'est pas installé. Veuillez l'installer avant de continuer."
    exit 1
fi

# Vérifier si pip est installé
if ! command -v pip3 &> /dev/null; then
    echo "pip3 n'est pas installé. Veuillez l'installer avant de continuer."
    exit 1
fi

# Créer et activer un environnement virtuel
echo "Création de l'environnement virtuel..."
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
echo "Installation des dépendances..."
pip3 install -r requirements.txt

# Créer les répertoires nécessaires
mkdir -p data logs

# Exécuter le scraper initial
echo "Collecte initiale des données..."
python3 -m scraper.scraper

# Rendre le script de mise à jour exécutable
chmod +x update_news.py

# Proposer de configurer cron
echo "Voulez-vous configurer la mise à jour automatique avec cron? (o/n)"
read -r setup_cron

if [ "$setup_cron" = "o" ] || [ "$setup_cron" = "O" ]; then
    # Créer un fichier crontab temporaire
    echo "Configuration de cron pour une mise à jour toutes les 3 heures..."
    crontab -l > mycron 2>/dev/null || echo "" > mycron
    echo "0 */3 * * * cd $(pwd) && ./venv/bin/python3 update_news.py" >> mycron
    crontab mycron
    rm mycron
    echo "Mise à jour automatique configurée."
fi

# Démarrer l'application Flask
echo "Démarrage du site web..."
cd website
python3 app.py