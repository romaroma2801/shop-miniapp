// footer.js - Футер с правильной синхронизацией навигации

/**
 * Установить активную вкладку футера
 */
window.setActiveFooter = function(section) {
    document.querySelectorAll('.footer-item').forEach(item => {
        const isActive = item.dataset.section === section;
        item.classList.toggle('active', isActive);
    });
    window.currentFooterSection = section;
    console.log(`Футер: активна вкладка "${section}"`);
};

/**
 * Инициализация футера
 */
function initFooter() {
    // Домой
    document.getElementById('home-button')?.addEventListener('click', () => {
        if (window.showHome) window.showHome();
    });
    
    // Каталог
    document.getElementById('catalog-button')?.addEventListener('click', () => {
        if (window.initCatalogPage) window.initCatalogPage();
    });
    
    // Корзина
    document.getElementById('cart-footer-button')?.addEventListener('click', () => {
        if (window.cart) window.cart.toggle();
    });
    
    // Акции
    document.getElementById('promotions-button')?.addEventListener('click', () => {
        if (window.showPromotions) window.showPromotions();
    });
    
    // Кабинет
    document.getElementById('login-button')?.addEventListener('click', () => {
        if (window.showUserPage) window.showUserPage();
    });
    
    // Инициализация корзины
    if (window.cart) {
        window.cart.updateBadge();
    }
    
    // Закрытие корзины при клике вне её
    document.addEventListener('click', (event) => {
        const cartOverlay = document.getElementById('cart-overlay');
        if (!cartOverlay || !cartOverlay.classList.contains('show')) return;
        
        const isClickInside = cartOverlay.contains(event.target);
        const isCartButton = event.target.closest('#cart-footer-button') || event.target.closest('.cart-button');
        
        if (!isClickInside && !isCartButton) {
            cartOverlay.classList.remove('show');
        }
    });
}

document.addEventListener('DOMContentLoaded', initFooter);
