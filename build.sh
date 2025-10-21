#!/bin/bash
set -e

echo "🐍 Installing Python dependencies..."
pip install -r requirements.txt

echo "🔨 Building static site..."
python3 build_static.py

echo "✅ Build complete!"
