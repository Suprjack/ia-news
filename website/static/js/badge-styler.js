/**
 * Dynamic badge styling based on category
 * Adds color-coded badges with icons for better visual hierarchy
 */

class BadgeStyler {
    constructor() {
        this.categoryStyles = {
            'llms': {
                color: '#ff6b9d',
                icon: 'fa-robot',
                label: 'LLMs & Models'
            },
            'tech': {
                color: '#00ffff',
                icon: 'fa-microchip',
                label: 'Technology'
            },
            'ml': {
                color: '#b000ff',
                icon: 'fa-brain',
                label: 'Machine Learning'
            },
            'hardware': {
                color: '#ffa500',
                icon: 'fa-server',
                label: 'Hardware'
            },
            'creative': {
                color: '#00ff88',
                icon: 'fa-palette',
                label: 'Creative AI'
            },
            'nocode': {
                color: '#ffaa00',
                icon: 'fa-puzzle-piece',
                label: 'No-Code'
            },
            'general': {
                color: '#888888',
                icon: 'fa-newspaper',
                label: 'General News'
            }
        };

        this.init();
    }

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.styleBadges());
        } else {
            this.styleBadges();
        }

        // Update badges when articles are filtered
        window.addEventListener('filterApplied', () => this.styleBadges());
    }

    /**
     * Style all visible article badges
     */
    styleBadges() {
        const badges = document.querySelectorAll('.card-category');

        badges.forEach(badge => {
            // Get category from parent card
            const card = badge.closest('.news-card');
            if (!card) return;

            const category = card.dataset.category || 'general';
            const style = this.categoryStyles[category] || this.categoryStyles['general'];

            // Check if badge already has proper styling
            if (badge.classList.contains('styled-badge')) return;

            // Clear existing content
            badge.innerHTML = '';

            // Create icon and text
            const icon = document.createElement('i');
            icon.className = `fas ${style.icon}`;

            const text = document.createElement('span');
            text.textContent = style.label;

            badge.appendChild(icon);
            badge.appendChild(text);

            // Apply styles
            badge.classList.add('styled-badge');
            badge.style.setProperty('--badge-color', style.color);

            // Create or update badge styles in head
            this.injectBadgeStyles(category, style.color);
        });
    }

    /**
     * Inject dynamic styles for badge colors
     */
    injectBadgeStyles(category, color) {
        let styleSheet = document.getElementById('badge-styles');

        if (!styleSheet) {
            styleSheet = document.createElement('style');
            styleSheet.id = 'badge-styles';
            document.head.appendChild(styleSheet);
        }

        const css = `
            .card-category[data-category="${category}"],
            .card-category.styled-badge {
                background: linear-gradient(135deg, ${color}22, ${color}11);
                border: 1px solid ${color}44;
                color: ${color};
                box-shadow: 0 0 20px ${color}22;
            }

            .card-category[data-category="${category}"]:hover,
            .card-category.styled-badge:hover {
                background: linear-gradient(135deg, ${color}33, ${color}22);
                box-shadow: 0 0 30px ${color}44};
                border-color: ${color}88;
            }
        `;

        // Only add if not already present
        if (!styleSheet.textContent.includes(category)) {
            styleSheet.textContent += css;
        }
    }

    /**
     * Update badge display when articles are loaded/changed
     */
    updateBadges() {
        this.styleBadges();
    }
}

// Initialize badge styler
const badgeStyler = new BadgeStyler();

// Listen for filter changes
document.addEventListener('DOMContentLoaded', () => {
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Trigger badge update after filter animation
            setTimeout(() => {
                window.dispatchEvent(new Event('filterApplied'));
            }, 400);
        });
    });
});
