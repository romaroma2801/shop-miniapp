class ModernFooter {
  constructor() {
    this.footer = document.querySelector('.footer-nav');
    this.indicator = document.querySelector('.footer-indicator');
    this.buttons = document.querySelectorAll('.footer-btn');
    this.activePage = 'home';
    
    this.init();
  }
  
  init() {
    this.setupEventListeners();
    this.setActiveButton(this.activePage);
    window.addEventListener('resize', () => this.updateIndicatorPosition());
  }
  
  setActiveButton(page) {
    this.activePage = page;
    
    this.buttons.forEach(btn => {
      const isActive = btn.dataset.page === page;
      btn.classList.toggle('active', isActive);
      
      if (isActive) {
        this.moveIndicator(btn);
      }
    });
  }
  
  moveIndicator(activeBtn) {
    const btnRect = activeBtn.getBoundingClientRect();
    const footerRect = this.footer.getBoundingClientRect();
    
    const left = btnRect.left - footerRect.left;
    const width = btnRect.width;
    
    this.indicator.style.left = `${left}px`;
    this.indicator.style.width = `${width}px`;
  }
  
  updateIndicatorPosition() {
    const activeBtn = document.querySelector(`.footer-btn.active`);
    if (activeBtn) {
      this.moveIndicator(activeBtn);
    }
  }
  
  setupEventListeners() {
    this.buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        const page = btn.dataset.page;
        
        if (page === this.activePage) return;
        
        if (page === 'cart') {
          if (typeof toggleCart === 'function') {
            toggleCart();
          }
          return;
        }
        
        this.setActiveButton(page);
        
        // Навигация по страницам
        if (page === 'home') goHome();
        else if (page === 'catalog') showSection('catalog');
        else if (page === 'promotions') showSection('promotions');
        else if (page === 'profile') showSection('user');
      });
    });
  }
  
  updateCartBadge(count) {
    const badge = document.querySelector('.cart-badge');
    if (badge) {
      badge.textContent = count > 9 ? '9+' : count;
      badge.style.display = count > 0 ? 'flex' : 'none';
    }
  }
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', () => {
  const footer = new ModernFooter();
  
  // Интеграция с корзиной
  if (window.cart) {
    window.cart.updateBadge = function() {
      const count = this.items.reduce((sum, item) => sum + item.quantity, 0);
      footer.updateCartBadge(count);
    };
    footer.updateCartBadge(window.cart.items.length);
  }
});
