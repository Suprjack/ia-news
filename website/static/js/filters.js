/**
 * Filter functionality for news articles
 * Handles category filtering with animations
 */

document.addEventListener('DOMContentLoaded', function() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const newsCards = document.querySelectorAll('.news-card:not(.trending-card)');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            filterBtns.forEach(b => b.classList.remove('active'));

            // Add active class to clicked button
            this.classList.add('active');

            const category = this.dataset.category;
            let visibleCount = 0;

            // Filter articles with staggered animation
            newsCards.forEach((card, index) => {
                const cardCategory = card.dataset.category;
                const isMatch = category === 'all' || cardCategory === category;

                if (isMatch) {
                    card.style.display = 'block';
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';

                    // Stagger the animation
                    setTimeout(() => {
                        card.style.transition = 'opacity 0.4s ease-out, transform 0.4s ease-out';
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, index * 30);

                    visibleCount++;
                } else {
                    card.style.transition = 'opacity 0.3s ease-out, transform 0.3s ease-out';
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(-10px)';

                    setTimeout(() => {
                        card.style.display = 'none';
                    }, 300);
                }
            });

            // Show/hide empty state
            const emptyState = document.getElementById('emptyState');
            if (visibleCount === 0 && emptyState) {
                emptyState.style.display = 'block';
                emptyState.style.opacity = '0';
                setTimeout(() => {
                    emptyState.style.transition = 'opacity 0.4s ease-out';
                    emptyState.style.opacity = '1';
                }, 10);
            } else if (emptyState) {
                emptyState.style.transition = 'opacity 0.3s ease-out';
                emptyState.style.opacity = '0';
                setTimeout(() => {
                    emptyState.style.display = 'none';
                }, 300);
            }
        });
    });
});
