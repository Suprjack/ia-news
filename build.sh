#!/bin/bash
set -e

echo "📦 Installing system dependencies for lxml..."
apt-get update
apt-get install -y libxml2-dev libxslt-dev

echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt

echo "🔨 Building static site..."
python3 build_static.py

echo "✅ Build complete!"
