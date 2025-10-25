/**
 * Content Translator
 * Handles French/English translation of article descriptions
 * Uses pre-translated content stored in data attributes
 */

class ContentTranslator {
    constructor() {
        this.currentLang = localStorage.getItem('language') || 'fr';
        this.init();
    }

    init() {
        // Listen for language changes
        window.addEventListener('languageChanged', (e) => {
            this.currentLang = e.detail.language;
            this.updateContent();
        });

        // Initial update on load
        this.updateContent();
    }

    /**
     * Update all article content based on current language
     */
    updateContent() {
        // Update card descriptions (homepage)
        this.updateCardDescriptions();

        // Update article descriptions (article pages)
        this.updateArticleDescription();

        // Update language note visibility
        this.updateLanguageNote();
    }

    /**
     * Update descriptions on news cards
     */
    updateCardDescriptions() {
        const cards = document.querySelectorAll('[data-description-en], [data-description-fr]');

        cards.forEach(card => {
            if (this.currentLang === 'fr' && card.hasAttribute('data-description-fr')) {
                card.textContent = card.getAttribute('data-description-fr');
            } else if (this.currentLang === 'en' && card.hasAttribute('data-description-en')) {
                card.textContent = card.getAttribute('data-description-en');
            }
        });
    }

    /**
     * Update article page description
     */
    updateArticleDescription() {
        const desc = document.querySelector('[data-article-description-en], [data-article-description-fr]');
        if (!desc) return;

        if (this.currentLang === 'fr' && desc.hasAttribute('data-article-description-fr')) {
            desc.textContent = desc.getAttribute('data-article-description-fr');
            desc.style.opacity = '0';
            setTimeout(() => {
                desc.style.transition = 'opacity 0.3s ease-in';
                desc.style.opacity = '1';
            }, 10);
        } else if (this.currentLang === 'en' && desc.hasAttribute('data-article-description-en')) {
            desc.textContent = desc.getAttribute('data-article-description-en');
            desc.style.opacity = '0';
            setTimeout(() => {
                desc.style.transition = 'opacity 0.3s ease-in';
                desc.style.opacity = '1';
            }, 10);
        }
    }

    /**
     * Show/hide language note based on language
     */
    updateLanguageNote() {
        const notes = document.querySelectorAll('.card-language-note, .article-language-banner');

        notes.forEach(note => {
            if (this.currentLang === 'en') {
                // Show language note in English when English is selected
                note.style.display = 'flex';
            } else {
                // Hide language note in French when French is selected (content is already FR)
                note.style.display = 'none';
            }
        });
    }
}

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    const translator = new ContentTranslator();

    // Also update when i18n is initialized
    if (window.i18n) {
        window.i18n.init = (function(original) {
            return async function() {
                await original.call(this);
                translator.updateContent();
            };
        })(window.i18n.init);
    }
});
