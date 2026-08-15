document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.card-carousel-group').forEach(function (group) {
        const carousel = group.querySelector('[data-card-carousel]');
        const previousButton = group.querySelector('.partner-carousel-prev');
        const nextButton = group.querySelector('.partner-carousel-next');
        const indicators = group.querySelector('.partner-carousel-indicators');
        let pageCount = 1;

        if (!carousel || !previousButton || !nextButton || !indicators) return;

        function pageWidth() {
            return Math.max(carousel.clientWidth, 1);
        }

        function currentPage() {
            const maxScroll = Math.max(0, carousel.scrollWidth - carousel.clientWidth);
            if (maxScroll === 0 || pageCount === 1) return 0;
            return Math.round((carousel.scrollLeft / maxScroll) * (pageCount - 1));
        }

        function updateControls() {
            const maxScroll = Math.max(0, carousel.scrollWidth - carousel.clientWidth);
            pageCount = Math.max(1, Math.ceil(carousel.scrollWidth / pageWidth()));
            const page = currentPage();
            const hasOverflow = maxScroll > 2;

            previousButton.hidden = !hasOverflow;
            nextButton.hidden = !hasOverflow;
            indicators.hidden = !hasOverflow;
            previousButton.disabled = carousel.scrollLeft <= 2;
            nextButton.disabled = carousel.scrollLeft >= maxScroll - 2;

            indicators.replaceChildren();
            if (hasOverflow) {
                for (let index = 0; index < pageCount; index += 1) {
                    const indicator = document.createElement('span');
                    indicator.className = 'partner-carousel-indicator' + (index === page ? ' active' : '');
                    indicators.appendChild(indicator);
                }
            }
        }

        function scrollToPage(direction) {
            const targetPage = Math.max(0, Math.min(pageCount - 1, currentPage() + direction));
            const maxScroll = Math.max(0, carousel.scrollWidth - carousel.clientWidth);
            const targetLeft = pageCount > 1 ? (targetPage / (pageCount - 1)) * maxScroll : 0;
            carousel.scrollTo({ left: targetLeft, behavior: 'smooth' });
        }

        previousButton.addEventListener('click', function () { scrollToPage(-1); });
        nextButton.addEventListener('click', function () { scrollToPage(1); });
        carousel.addEventListener('scroll', function () {
            window.requestAnimationFrame(updateControls);
        }, { passive: true });

        if ('ResizeObserver' in window) {
            new ResizeObserver(updateControls).observe(carousel);
        } else {
            window.addEventListener('resize', updateControls);
        }
        updateControls();
    });
});
