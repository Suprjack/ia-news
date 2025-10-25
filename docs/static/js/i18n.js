/**
 * Simple i18n system for AI News
 * Supports FR (default) and EN
 * Uses localStorage for persistence
 */

class I18n {
    constructor() {
        this.translations = {};
        this.currentLanguage = localStorage.getItem('language') || 'fr';
        this.init();
    }

    async init() {
        try {
            const response = await fetch('/static/i18n/translations.json');
            this.translations = await response.json();
            this.applyLanguage();
        } catch (error) {
            console.error('Error loading translations:', error);
        }
    }

    /**
     * Get translated string
     * Supports nested keys: "nav.home"
     * Supports interpolation: "Found {{count}} results"
     */
    t(key, params = {}) {
        const keys = key.split('.');
        let value = this.translations[this.currentLanguage];

        for (const k of keys) {
            if (value && typeof value === 'object') {
                value = value[k];
            } else {
                console.warn(`Translation key not found: ${key}`);
                return key;
            }
        }

        // Handle interpolation
        if (typeof value === 'string' && Object.keys(params).length > 0) {
            Object.keys(params).forEach(param => {
                value = value.replace(`{{${param}}}`, params[param]);
            });
        }

        return value || key;
    }

    /**
     * Set language and update all translatable elements
     */
    setLanguage(lang) {
        if (lang === 'fr' || lang === 'en') {
            this.currentLanguage = lang;
            localStorage.setItem('language', lang);
            this.applyLanguage();

            // Trigger language changed event
            window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
        }
    }

    /**
     * Apply translations to all elements with data-i18n attribute
     */
    applyLanguage() {
        // Update elements with data-i18n
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            const params = element.getAttribute('data-i18n-params');
            const parsedParams = params ? JSON.parse(params) : {};
            element.textContent = this.t(key, parsedParams);
        });

        // Update placeholder attributes
        document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
            const key = element.getAttribute('data-i18n-placeholder');
            element.placeholder = this.t(key);
        });

        // Update title attributes
        document.querySelectorAll('[data-i18n-title]').forEach(element => {
            const key = element.getAttribute('data-i18n-title');
            element.title = this.t(key);
        });

        // Update aria-label
        document.querySelectorAll('[data-i18n-aria-label]').forEach(element => {
            const key = element.getAttribute('data-i18n-aria-label');
            element.setAttribute('aria-label', this.t(key));
        });

        // Update HTML content (for inline elements)
        document.querySelectorAll('[data-i18n-html]').forEach(element => {
            const key = element.getAttribute('data-i18n-html');
            const params = element.getAttribute('data-i18n-params');
            const parsedParams = params ? JSON.parse(params) : {};
            element.innerHTML = this.t(key, parsedParams);
        });

        // Update current language indicator
        document.querySelectorAll('.language-toggle').forEach(btn => {
            btn.classList.remove('active');
            if (btn.getAttribute('data-language') === this.currentLanguage) {
                btn.classList.add('active');
            }
        });

        // Update HTML lang attribute
        document.documentElement.lang = this.currentLanguage;
    }

    /**
     * Get current language
     */
    getCurrentLanguage() {
        return this.currentLanguage;
    }

    /**
     * Check if language is French
     */
    isFrench() {
        return this.currentLanguage === 'fr';
    }

    /**
     * Check if language is English
     */
    isEnglish() {
        return this.currentLanguage === 'en';
    }
}

// Initialize i18n globally
const i18n = new I18n();

// Keyboard shortcut for language toggle: Ctrl/Cmd + Shift + L
document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'L') {
        e.preventDefault();
        const newLang = i18n.getCurrentLanguage() === 'fr' ? 'en' : 'fr';
        i18n.setLanguage(newLang);
    }
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = i18n;
}
