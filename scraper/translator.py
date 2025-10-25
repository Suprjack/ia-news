#!/usr/bin/env python3
"""
Translator module for article content
Uses free translation APIs to translate article descriptions to French
Supports fallback mechanisms
"""

import os
import json
import time
import requests
from typing import Optional, Dict

class ArticleTranslator:
    """Translate article content to French using multiple fallback methods"""

    def __init__(self, cache_file: str = 'data/translation_cache.json'):
        self.cache_file = cache_file
        self.cache = self.load_cache()
        self.translation_count = 0

    def load_cache(self) -> Dict:
        """Load cached translations to avoid re-translating"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_cache(self):
        """Save cache to file"""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def translate_text(self, text: str, source_lang: str = 'en', target_lang: str = 'fr') -> Optional[str]:
        """
        Translate text using multiple fallback methods
        1. Check cache first
        2. Try MyMemory free API (no key needed)
        3. Return original if all fail
        """
        if not text or len(text.strip()) < 10:
            return text

        # Create cache key
        cache_key = f"{source_lang}-{target_lang}:{text[:100]}"

        # Check cache
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Try translation
        translated = self._translate_with_mymemory(text, source_lang, target_lang)

        if translated and translated != text:
            self.cache[cache_key] = translated
            self.translation_count += 1
            # Auto-save every 10 translations
            if self.translation_count % 10 == 0:
                self.save_cache()
            return translated

        return text

    def _translate_with_mymemory(self, text: str, source_lang: str = 'en', target_lang: str = 'fr') -> Optional[str]:
        """
        Use MyMemory API (free, no auth required)
        No rate limiting for reasonable use
        """
        try:
            # Split text if too long (API limit ~500 chars)
            if len(text) > 500:
                # Translate in chunks, respecting sentence boundaries
                sentences = text.split('. ')
                translated_sentences = []
                for sentence in sentences:
                    if sentence.strip():
                        trans = self._translate_with_mymemory(sentence, source_lang, target_lang)
                        translated_sentences.append(trans if trans else sentence)
                return '. '.join(translated_sentences)

            url = 'https://api.mymemory.translated.net/get'
            params = {
                'q': text,
                'langpair': f'{source_lang}|{target_lang}'
            }

            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if data.get('responseStatus') == 200:
                    translated = data.get('responseData', {}).get('translatedText', '')
                    if translated and translated != text:
                        return translated

            return None
        except Exception as e:
            print(f"Translation error: {e}")
            return None

    def translate_article(self, article: Dict) -> Dict:
        """Translate article description and title"""
        article_copy = article.copy()

        # Translate description
        if article.get('description'):
            translated_desc = self.translate_text(article['description'])
            article_copy['description_fr'] = translated_desc

        # Translate title (if we want to be thorough)
        if article.get('title'):
            translated_title = self.translate_text(article['title'])
            article_copy['title_fr'] = translated_title

        return article_copy

    def finalize(self):
        """Save final cache before exit"""
        self.save_cache()
        print(f"✅ Translated {self.translation_count} article descriptions")


def translate_articles(articles: list) -> list:
    """Main function to translate all articles"""
    print("🌍 Starting article translation to French...")

    translator = ArticleTranslator()
    translated_articles = []

    for i, article in enumerate(articles):
        # Show progress
        if (i + 1) % 10 == 0:
            print(f"   Translated {i + 1}/{len(articles)} articles...")

        translated = translator.translate_article(article)
        translated_articles.append(translated)

        # Small delay to avoid rate limiting
        if i % 5 == 0:
            time.sleep(0.1)

    translator.finalize()
    return translated_articles


if __name__ == '__main__':
    # Test translation
    test_article = {
        'title': 'OpenAI releases new GPT model',
        'description': 'OpenAI has announced a new version of their language model with improved capabilities.'
    }

    translator = ArticleTranslator()
    translated = translator.translate_article(test_article)
    print("Original:", test_article)
    print("Translated:", translated)
    translator.finalize()
